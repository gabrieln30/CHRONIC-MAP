from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base, utcnow


class TentativaRecuperacao(Base):
    """Uma linha por tentativa FALHA de "esqueci a senha" (para travar força bruta no CPF).

    Guarda só o e-mail digitado e a hora; não guarda CPF nem senha. Linhas com mais de
    24 h são apagadas a cada chamada da rota.
    """

    __tablename__ = "tentativa_recuperacao"

    id        = Column(Integer, primary_key=True, autoincrement=True)
    email     = Column(String(150), nullable=False, index=True)
    criado_em = Column(DateTime, nullable=False, default=utcnow, index=True)
