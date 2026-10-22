import enum

from sqlalchemy import Column, Integer, Text, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base, utcnow


class NivelConhecimento(str, enum.Enum):
    iniciante     = "iniciante"
    intermediario = "intermediario"
    avancado      = "avancado"


class EstiloAprendizado(str, enum.Enum):
    visual  = "visual"
    pratico = "pratico"
    leitura = "leitura"
    video   = "video"


class ExperienciaPrevia(str, enum.Enum):
    nenhuma           = "nenhuma"
    projetos_pessoais = "projetos_pessoais"
    profissional      = "profissional"


class Diagnostico(Base):
    __tablename__ = "diagnostico"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id          = Column(Integer, ForeignKey("usuario.id",    ondelete="CASCADE",  onupdate="CASCADE"), nullable=False, index=True)
    area_micro_id       = Column(Integer, ForeignKey("area_micro.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    nivel_conhecimento  = Column(Enum(NivelConhecimento), nullable=False)
    tempo_semanal_horas = Column(Integer,                 nullable=False)
    objetivo            = Column(Text,                    nullable=False)
    estilo_aprendizado  = Column(Enum(EstiloAprendizado), nullable=False)
    # Resposta da 5ª pergunta do questionário (antes não tinha onde ser salva).
    experiencia_previa  = Column(Enum(ExperienciaPrevia), nullable=True)
    criado_em           = Column(DateTime, nullable=False, default=utcnow)

    usuario    = relationship("Usuario",   back_populates="diagnosticos")
    area_micro = relationship("AreaMicro", back_populates="diagnosticos")
    trilha     = relationship("Trilha",    back_populates="diagnostico", uselist=False, cascade="all, delete")
