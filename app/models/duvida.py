from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship

from app.database import Base, utcnow


class Duvida(Base):
    __tablename__ = "duvida"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id       = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    trilha_id        = Column(Integer, ForeignKey("trilha.id",  ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    etapa_referencia = Column(Integer, nullable=True)
    pergunta         = Column(Text,    nullable=False)
    resposta_json    = Column(JSON,    nullable=False)
    criado_em        = Column(DateTime, nullable=False, default=utcnow)

    usuario = relationship("Usuario", back_populates="duvidas")
    trilha  = relationship("Trilha",  back_populates="duvidas")
