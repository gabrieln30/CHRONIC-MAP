import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, trilha_do_usuario
from app.models.diagnostico import Diagnostico
from app.models.progresso import Progresso
from app.models.trilha import Trilha
from app.models.usuario import Usuario
from app.schemas import TrilhaGerarIn, TrilhaOut
from app.services import ia_service

logger = logging.getLogger("chronic_map.trilha")
router = APIRouter(prefix="/trilha", tags=["Trilha"])


@router.post("/gerar", response_model=TrilhaOut, status_code=201)
def gerar_trilha_personalizada(
    dados: TrilhaGerarIn,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """
    Recebe o ID do diagnóstico, chama a IA (Gemini) e salva a trilha gerada.
    Também já cria o registro de progresso (etapa 0) dessa trilha.
    """
    diag = (
        db.query(Diagnostico)
        .filter(Diagnostico.id == dados.diagnostico_id, Diagnostico.usuario_id == usuario.id)
        .first()
    )
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnóstico não encontrado.")

    if db.query(Trilha).filter(Trilha.diagnostico_id == diag.id).first():
        raise HTTPException(status_code=409, detail="Já existe uma trilha gerada para esse diagnóstico.")

    # Copia os dados para variáveis simples e fecha a transação ANTES de chamar a IA,
    # para não segurar uma conexão do banco durante os segundos da chamada externa.
    diag_id = diag.id
    area_macro = diag.area_micro.area_macro.nome
    area_micro = diag.area_micro.nome
    perfil = {
        "nivel": diag.nivel_conhecimento.value,
        "horas": diag.tempo_semanal_horas,
        "objetivo": diag.objetivo,
        "estilo": diag.estilo_aprendizado.value,
        "experiencia": diag.experiencia_previa.value if diag.experiencia_previa else None,
    }
    db.rollback()

    try:
        conteudo = ia_service.gerar_trilha(area_macro=area_macro, area_micro=area_micro, diagnostico=perfil)
    except ia_service.IAServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception:
        logger.exception("Erro inesperado ao gerar a trilha")
        raise HTTPException(status_code=502, detail="Falha ao comunicar com a IA. Tente novamente.")

    nova = Trilha(diagnostico_id=diag_id, conteudo_json=conteudo)
    nova.progresso = Progresso(usuario_id=usuario.id, etapa_atual=0, exercicios_concluidos=[])
    db.add(nova)
    try:
        db.commit()
    except IntegrityError:  # dois cliques simultâneos geraram duas trilhas
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe uma trilha gerada para esse diagnóstico.")
    db.refresh(nova)
    return nova


@router.get("/{trilha_id}", response_model=TrilhaOut)
def buscar_trilha(
    trilha_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Retorna uma trilha salva (somente se for do usuário logado)."""
    return trilha_do_usuario(db, trilha_id, usuario)


@router.delete("/{trilha_id}", status_code=204)
def deletar_trilha(
    trilha_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Remove a trilha para refazê-la (RF11).

    Atenção: o progresso e o histórico de dúvidas DESSA trilha são apagados junto.
    O diagnóstico é mantido, então dá para gerar uma nova trilha a partir dele.
    """
    trilha = trilha_do_usuario(db, trilha_id, usuario)
    db.delete(trilha)
    db.commit()
