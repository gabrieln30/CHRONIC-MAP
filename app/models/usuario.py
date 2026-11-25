from sqlalchemy import Column, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base, utcnow


class Usuario(Base):
    __tablename__ = "usuario"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    nome       = Column(String(100), nullable=False)
    email      = Column(String(150), nullable=False, unique=True)
    senha_hash = Column(String(255), nullable=False)
    # "comum" (padrão) ou "master". Só é alterado direto no banco (Supabase), nunca pela API.
    perfil     = Column(String(10), nullable=False, default="comum", server_default="comum")
    # Dados do cadastro. Senha, CPF e resposta de 2FA nunca são armazenados em texto puro.
    nascimento    = Column(Date, nullable=True)
    sexo          = Column(String(1), nullable=True)
    nome_mae_hash = Column(String(255), nullable=True)
    cpf_hash      = Column(String(255), nullable=True)
    celular       = Column(String(20), nullable=True)
    telefone_fixo = Column(String(20), nullable=True)
    cep           = Column(String(9), nullable=True)
    logradouro    = Column(String(150), nullable=True)
    numero        = Column(String(20), nullable=True)
    bairro        = Column(String(100), nullable=True)
    cidade        = Column(String(100), nullable=True)
    uf            = Column(String(2), nullable=True)
    criado_em  = Column(DateTime, nullable=False, default=utcnow)
    # Foto de perfil: data URL (JPEG/PNG/WebP, já reduzida pelo front). Fica no banco; NULL = sem foto.
    foto       = Column(Text, nullable=True)

    diagnosticos = relationship("Diagnostico", back_populates="usuario", cascade="all, delete")
    progressos   = relationship("Progresso",   back_populates="usuario", cascade="all, delete")
    duvidas      = relationship("Duvida",      back_populates="usuario", cascade="all, delete")
