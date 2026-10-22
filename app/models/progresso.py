from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship

from app.database import Base, utcnow


class Progresso(Base):
    __tablename__ = "progresso"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    trilha_id  = Column(
        Integer,
        ForeignKey("trilha.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        unique=True,  # Trilha 1:1 Progresso
    )
    usuario_id = Column(
        Integer,
        ForeignKey("usuario.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    etapa_atual = Column(Integer, nullable=False, default=0)
    # Lista de ids "etapa-indice" (ex.: "0-1" = exercício 1 da etapa 0).
    exercicios_concluidos = Column(JSON, nullable=False, default=list)
    atualizado_em = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    trilha  = relationship("Trilha",  back_populates="progresso")
    usuario = relationship("Usuario", back_populates="progressos")
