"""Popula as áreas (RF01/RF02) na primeira inicialização, se a tabela estiver vazia."""
from sqlalchemy.orm import Session

from app.models.area_macro import AreaMacro
from app.models.area_micro import AreaMicro

AREAS = {
    "TI": [
        "Desenvolvimento Web", "Desenvolvimento Mobile", "Dados e Inteligência Artificial",
        "Redes e Infraestrutura", "Segurança da Informação", "Cloud e DevOps",
    ],
    "Saúde": [
        "Farmácia", "Enfermagem", "Nutrição", "Fisioterapia", "Gestão em Saúde",
    ],
    "Administração": [
        "Finanças", "Marketing", "Recursos Humanos", "Logística", "Empreendedorismo",
    ],
    "Engenharia": [
        "Civil", "Elétrica", "Mecânica", "de Produção", "de Software",
    ],
}


def popular_areas(db: Session) -> int:
    """Insere as áreas padrão. Retorna quantas áreas macro foram criadas."""
    if db.query(AreaMacro).count() > 0:
        return 0
    for nome_macro, subs in AREAS.items():
        macro = AreaMacro(nome=nome_macro)
        macro.subareas = [AreaMicro(nome=s) for s in subs]
        db.add(macro)
    db.commit()
    return len(AREAS)
