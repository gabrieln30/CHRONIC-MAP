from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class AreaMacro(Base):
    __tablename__ = "area_macro"

    id   = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False, unique=True)

    subareas = relationship(
        "AreaMicro",
        back_populates="area_macro",
        cascade="all, delete",
        order_by="AreaMicro.nome",
    )
