from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class AreaMicro(Base):
    __tablename__ = "area_micro"
    __table_args__ = (
        UniqueConstraint("area_macro_id", "nome", name="uq_area_micro_macro_nome"),
    )

    id            = Column(Integer, primary_key=True, autoincrement=True)
    nome          = Column(String(100), nullable=False)
    area_macro_id = Column(
        Integer,
        ForeignKey("area_macro.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    area_macro   = relationship("AreaMacro",   back_populates="subareas")
    diagnosticos = relationship("Diagnostico", back_populates="area_micro")
