"""Consulta dos logs de autenticação (somente master)."""
import re
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import exigir_master
from app.models.log_acesso import LogAcesso
from app.models.usuario import Usuario
from app.schemas import LogOut
from app.security import verificar_senha

router = APIRouter(prefix="/logs", tags=["Logs (admin)"])


@router.get("", response_model=list[LogOut])
def listar(
    campo: Literal["todos", "nome", "cpf"] = "todos",
    q: str = Query(default="", max_length=100),
    limite: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(exigir_master),
):
    """Acessos dos usuários comuns, do mais recente ao mais antigo."""
    consulta = (
        db.query(LogAcesso)
        .join(Usuario, Usuario.id == LogAcesso.usuario_id)
        .filter(Usuario.perfil != "master")
    )

    termo = q.strip()
    if campo == "nome" and termo:
        seguro = termo.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        consulta = consulta.filter(LogAcesso.nome.ilike(f"%{seguro}%", escape="\\"))

    elif campo == "cpf" and termo:
        # O CPF só existe como hash com salt (não dá para buscar direto no SQL),
        # então comparamos o CPF digitado com o hash de cada usuário que tem CPF.
        digitos = re.sub(r"\D", "", termo)
        if len(digitos) != 11:
            return []
        candidatos = (
            db.query(Usuario.id, Usuario.cpf_hash)
            .filter(Usuario.cpf_hash.isnot(None), Usuario.perfil != "master")
            .all()
        )
        ids = [uid for uid, h in candidatos if verificar_senha(digitos, h)]
        if not ids:
            return []
        consulta = consulta.filter(LogAcesso.usuario_id.in_(ids))

    return consulta.order_by(LogAcesso.criado_em.desc()).limit(limite).all()
