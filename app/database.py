"""Conexão com o MySQL (SQLAlchemy).

Lê a DATABASE_URL do ambiente (.env), cria o engine, a SessionLocal usada em
cada requisição e a Base da qual todos os models herdam.
"""
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não definida. Copie o .env.example para .env e preencha "
        "(ex.: mysql+pymysql://usuario:senha@db:3306/trilha_db?charset=utf8mb4)."
    )

_engine_kwargs = {"pool_pre_ping": True}  # evita 'MySQL server has gone away'
if DATABASE_URL.startswith("sqlite"):
    # Só usado nos testes automatizados.
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _engine_kwargs["pool_recycle"] = 1800

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def utcnow() -> datetime:
    """UTC 'ingênuo' (sem tzinfo), compatível com DateTime do MySQL.

    Substitui datetime.utcnow(), deprecado a partir do Python 3.12.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_db():
    """Dependência do FastAPI: uma sessão por requisição, sempre fechada."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
