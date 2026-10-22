"""Hash de senhas (bcrypt) e tokens JWT.

A SECRET_KEY vem do .env e é obrigatória: sem ela a API não sobe, em vez de
rodar com uma chave padrão previsível.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 16:
    raise RuntimeError(
        "SECRET_KEY ausente ou curta demais (mínimo 16 caracteres). "
        "Gere uma com: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash "de mentira" usado para gastar o mesmo tempo quando o e-mail não existe
# (evita descobrir e-mails cadastrados medindo o tempo de resposta do login).
_DUMMY_HASH = _pwd_context.hash("senha-inexistente-apenas-para-timing")


def hash_senha(senha: str) -> str:
    return _pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: Optional[str]) -> bool:
    if senha_hash is None:
        _pwd_context.verify(senha, _DUMMY_HASH)
        return False
    return _pwd_context.verify(senha, senha_hash)


def criar_token(usuario_id: int) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(usuario_id), "exp": expira}, SECRET_KEY, algorithm=ALGORITHM)


def ler_token(token: str) -> Optional[int]:
    """Devolve o id do usuário do token, ou None se inválido/expirado."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None
