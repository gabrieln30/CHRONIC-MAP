from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, trilha_do_usuario
from app.models.usuario import Usuario
from app.schemas import EtapaUpdate, ExercicioUpdate, ProgressoOut

router = APIRouter(prefix="/progresso", tags=["Progresso"])


def _etapas(trilha) -> list[dict]:
    return (trilha.conteudo_json or {}).get("etapas", [])


@router.get("/{trilha_id}", response_model=ProgressoOut)
def buscar_progresso(
    trilha_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Retorna o progresso atual do usuário em uma trilha."""
    trilha = trilha_do_usuario(db, trilha_id, usuario)
    if not trilha.progresso:
        raise HTTPException(status_code=404, detail="Progresso não encontrado para essa trilha.")
    return trilha.progresso


@router.patch("/{trilha_id}/etapa", response_model=ProgressoOut)
def atualizar_etapa(
    trilha_id: int,
    dados: EtapaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Define a etapa atual (0 até o nº de etapas; igual ao nº de etapas = trilha concluída)."""
    trilha = trilha_do_usuario(db, trilha_id, usuario)
    prog = trilha.progresso
    if not prog:
        raise HTTPException(status_code=404, detail="Progresso não encontrado.")

    total = len(_etapas(trilha))
    if dados.etapa_atual > total:
        raise HTTPException(status_code=422, detail=f"etapa_atual deve estar entre 0 e {total}.")

    prog.etapa_atual = dados.etapa_atual
    db.commit()
    db.refresh(prog)
    return prog


@router.patch("/{trilha_id}/exercicio", response_model=ProgressoOut)
def concluir_exercicio(
    trilha_id: int,
    dados: ExercicioUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Marca um exercício (etapa + índice) como concluído. Repetir a chamada é inofensivo."""
    trilha = trilha_do_usuario(db, trilha_id, usuario)
    prog = trilha.progresso
    if not prog:
        raise HTTPException(status_code=404, detail="Progresso não encontrado.")

    etapas = _etapas(trilha)
    if dados.etapa >= len(etapas):
        raise HTTPException(status_code=422, detail="Etapa inexistente nessa trilha.")
    if dados.indice >= len(etapas[dados.etapa].get("exercicios", [])):
        raise HTTPException(status_code=422, detail="Exercício inexistente nessa etapa.")

    chave = f"{dados.etapa}-{dados.indice}"
    concluidos = list(prog.exercicios_concluidos or [])
    if chave not in concluidos:
        # Atribui uma lista NOVA: mudar a lista antiga "no lugar" não é detectado
        # pelo SQLAlchemy em colunas JSON e o UPDATE nunca seria enviado.
        prog.exercicios_concluidos = [*concluidos, chave]
        db.commit()
        db.refresh(prog)
    return prog
