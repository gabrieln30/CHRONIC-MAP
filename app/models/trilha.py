from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship

from app.database import Base, utcnow


class Trilha(Base):
    __tablename__ = "trilha"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    diagnostico_id = Column(
        Integer,
        ForeignKey("diagnostico.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        unique=True,  # Diagnostico 1:1 Trilha
    )
    conteudo_json = Column(JSON, nullable=False)
    criado_em     = Column(DateTime, nullable=False, default=utcnow)

    diagnostico = relationship("Diagnostico", back_populates="trilha")
    progresso   = relationship("Progresso", back_populates="trilha", uselist=False, cascade="all, delete")
    duvidas     = relationship("Duvida",    back_populates="trilha", cascade="all, delete")
