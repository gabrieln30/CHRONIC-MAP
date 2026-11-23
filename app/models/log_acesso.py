from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base, utcnow


class LogAcesso(Base):
    """Um registro por login bem-sucedido. Não guarda CPF, senha nem IP."""

    __tablename__ = "log_acesso"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id    = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False, index=True)
    nome          = Column(String(100), nullable=False)   # nome no momento do acesso
    segundo_fator = Column(String(50), nullable=True)     # fica vazio enquanto o login não tiver 2FA
    criado_em     = Column(DateTime, nullable=False, default=utcnow, index=True)
