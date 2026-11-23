"""Rotas de administração de usuários (somente master)."""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import eh_master, exigir_master
from app.models.usuario import Usuario
from app.schemas import PerfilUpdate, UsuarioListaOut

router = APIRouter(prefix="/usuarios", tags=["Usuários (admin)"])


@router.get("", response_model=list[UsuarioListaOut])
def listar(
    q: str = Query(default="", max_length=100),
    db: Session = Depends(get_db),
    _: Usuario = Depends(exigir_master),
):
    """Lista os usuários (comuns e masters), com busca opcional por trecho do nome."""
    consulta = db.query(Usuario)

    termo = q.strip()
    if termo:
        # Escapa % e _ para que sejam buscados como texto comum.
        seguro = termo.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        consulta = consulta.filter(Usuario.nome.ilike(f"%{seguro}%", escape="\\"))

    return consulta.order_by(Usuario.criado_em.desc()).all()


@router.patch("/{usuario_id}/perfil", response_model=UsuarioListaOut)
def alterar_perfil(
    usuario_id: int,
    dados: PerfilUpdate,
    db: Session = Depends(get_db),
    atual: Usuario = Depends(exigir_master),
):
    """Promove um usuário a master ou o devolve a comum. Ninguém altera o próprio perfil."""
    alvo = db.get(Usuario, usuario_id)
    if alvo is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if alvo.id == atual.id:
        # Evita que o último master se rebaixe e deixe o sistema sem administrador.
        raise HTTPException(status_code=403, detail="Você não pode alterar o seu próprio perfil.")
    alvo.perfil = dados.perfil
    db.commit()
    db.refresh(alvo)
    return alvo


@router.delete("/{usuario_id}", status_code=204)
def excluir(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(exigir_master),
):
    """Exclui o usuário e, em cascata, diagnósticos, progresso e dúvidas dele."""
    alvo = db.get(Usuario, usuario_id)
    if alvo is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if eh_master(alvo):
        raise HTTPException(status_code=403, detail="Não é possível excluir um administrador. Rebaixe-o antes.")
    db.delete(alvo)
    db.commit()
    return Response(status_code=204)
