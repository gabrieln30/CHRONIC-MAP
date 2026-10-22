from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base, utcnow


class Usuario(Base):
    __tablename__ = "usuario"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    nome       = Column(String(100), nullable=False)
    email      = Column(String(150), nullable=False, unique=True)
    senha_hash = Column(String(255), nullable=False)
    criado_em  = Column(DateTime, nullable=False, default=utcnow)

    diagnosticos = relationship("Diagnostico", back_populates="usuario", cascade="all, delete")
    progressos   = relationship("Progresso",   back_populates="usuario", cascade="all, delete")
    duvidas      = relationship("Duvida",      back_populates="usuario", cascade="all, delete")
