import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, trilha_do_usuario
from app.models.duvida import Duvida
from app.models.usuario import Usuario
from app.schemas import DuvidaIn, DuvidaOut
from app.services import assistente_service
from app.services.ia_service import IAServiceError

logger = logging.getLogger("chronic_map.assistente")
router = APIRouter(prefix="/assistente", tags=["Assistente IA"])


@router.post("/perguntar", response_model=DuvidaOut, status_code=201)
def fazer_pergunta(
    dados: DuvidaIn,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """
    Recebe a dúvida, monta o contexto completo (área, nível, etapa atual)
    e retorna a resposta da IA com diagnóstico, plano e materiais sugeridos.
    """
    trilha = trilha_do_usuario(db, dados.trilha_id, usuario)

    etapa_atual = trilha.progresso.etapa_atual if trilha.progresso else 0
    diag = trilha.diagnostico
    contexto = {
        "area_macro": diag.area_micro.area_macro.nome,
        "area_micro": diag.area_micro.nome,
        "nivel": diag.nivel_conhecimento.value,
        "horas": diag.tempo_semanal_horas,
        "objetivo": diag.objetivo,
        "estilo": diag.estilo_aprendizado.value,
        "etapa_atual": etapa_atual,
    }
    trilha_id = trilha.id
    db.rollback()  # libera a conexão do banco enquanto esperamos a IA

    try:
        resposta = assistente_service.responder_duvida(pergunta=dados.pergunta, contexto=contexto)
    except IAServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception:
        logger.exception("Erro inesperado no assistente")
        raise HTTPException(status_code=502, detail="Falha ao comunicar com a IA. Tente novamente.")

    nova = Duvida(
        usuario_id=usuario.id,
        trilha_id=trilha_id,
        etapa_referencia=etapa_atual,
        pergunta=dados.pergunta,
        resposta_json=resposta,
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


@router.get("/historico/{usuario_id}", response_model=list[DuvidaOut])
def historico_duvidas(
    usuario_id: int,
    trilha_id: int | None = Query(default=None, gt=0),
    limite: int = Query(default=50, ge=1, le=200),
    deslocamento: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Histórico de perguntas e respostas. Só é possível ver o PRÓPRIO histórico."""
    if usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="Você só pode ver o seu próprio histórico.")

    consulta = db.query(Duvida).filter(Duvida.usuario_id == usuario.id)
    if trilha_id is not None:
        consulta = consulta.filter(Duvida.trilha_id == trilha_id)
    return (
        consulta.order_by(Duvida.criado_em.desc(), Duvida.id.desc())
        .offset(deslocamento)
        .limit(limite)
        .all()
    )
