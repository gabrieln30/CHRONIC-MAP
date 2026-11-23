"""Dependências compartilhadas pelos routers: usuário logado e checagem de dono."""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.diagnostico import Diagnostico
from app.models.trilha import Trilha
from app.models.usuario import Usuario
from app.security import ler_token

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    cred: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autenticado ou token inválido/expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if cred is None:
        raise erro
    usuario_id = ler_token(cred.credentials)
    if usuario_id is None:
        raise erro
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise erro
    return usuario


def trilha_do_usuario(db: Session, trilha_id: int, usuario: Usuario) -> Trilha:
    """Busca a trilha SOMENTE se pertencer ao usuário logado.

    Devolve 404 (e não 403) também quando a trilha é de outra pessoa, para não
    revelar quais ids existem.
    """
    trilha = (
        db.query(Trilha)
        .join(Diagnostico, Trilha.diagnostico_id == Diagnostico.id)
        .filter(Trilha.id == trilha_id, Diagnostico.usuario_id == usuario.id)
        .first()
    )
    if trilha is None:
        raise HTTPException(status_code=404, detail="Trilha não encontrada.")
    return trilha


def eh_master(usuario: Usuario) -> bool:
    """O perfil fica na coluna usuario.perfil e só é alterado direto no banco."""
    return usuario.perfil == "master"


def exigir_master(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    """Só deixa passar o master; qualquer outro usuário recebe 403."""
    if not eh_master(usuario):
        raise HTTPException(status_code=403, detail="Acesso restrito ao administrador.")
    return usuario
