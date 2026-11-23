from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.area_macro import AreaMacro
from app.models.area_micro import AreaMicro
from app.schemas import AreaMacroOut, AreaMicroOut

router = APIRouter(prefix="/areas", tags=["Áreas"])


@router.get("", response_model=list[AreaMacroOut])
def listar_areas_macro(db: Session = Depends(get_db)):
    """Retorna todas as áreas macro (lista vazia se ainda não houver nenhuma)."""
    return db.query(AreaMacro).order_by(AreaMacro.nome).all()


@router.get("/{area_macro_id}/subareas", response_model=list[AreaMicroOut])
def listar_subareas(area_macro_id: int, db: Session = Depends(get_db)):
    """Retorna as subáreas de uma área macro específica."""
    if not db.get(AreaMacro, area_macro_id):
        raise HTTPException(status_code=404, detail="Área macro não encontrada.")
    return (
        db.query(AreaMicro)
        .filter(AreaMicro.area_macro_id == area_macro_id)
        .order_by(AreaMicro.nome)
        .all()
    )
