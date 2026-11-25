"""Ponto de entrada da API (uvicorn app.main:app)."""
import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app import models  # noqa: F401  (registra TODOS os models na Base)
from app.database import Base, SessionLocal, engine
from app.routers import areas, assistente, auth, diagnostico, logs, progresso, trilha, usuarios
from app.seed import popular_areas

logger = logging.getLogger("chronic_map")


def _atualizar_schema_usuario_legado() -> None:
    """Acrescenta os campos de cadastro em instalações Supabase já existentes.

    Projetos novos recebem essas colunas pelo ``create_all``; esta etapa evita que
    instalações feitas antes da integração quebrem ao receber o formulário completo.
    """
    if engine.dialect.name != "postgresql":
        return
    colunas = {
        "perfil": "VARCHAR(10) NOT NULL DEFAULT 'comum'",
        "nascimento": "DATE",
        "sexo": "VARCHAR(1)",
        "nome_mae_hash": "VARCHAR(255)",
        "cpf_hash": "VARCHAR(255)",
        "celular": "VARCHAR(20)",
        "telefone_fixo": "VARCHAR(20)",
        "cep": "VARCHAR(9)",
        "logradouro": "VARCHAR(150)",
        "numero": "VARCHAR(20)",
        "bairro": "VARCHAR(100)",
        "cidade": "VARCHAR(100)",
        "uf": "VARCHAR(2)",
        "foto": "TEXT",
    }
    with engine.begin() as conn:
        for nome, tipo in colunas.items():
            conn.execute(text(f"ALTER TABLE usuario ADD COLUMN IF NOT EXISTS {nome} {tipo}"))


def _esperar_banco(tentativas: int = 5, intervalo: float = 2.0) -> None:
    """Espera o banco remoto/local aceitar conexões antes de inicializar a API."""
    for n in range(1, tentativas + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except OperationalError as exc:
            logger.warning("Banco indisponível (tentativa %s/%s): %s", n, tentativas, exc.__class__.__name__)
            if n == tentativas:
                raise
            time.sleep(intervalo)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _esperar_banco()
    Base.metadata.create_all(bind=engine)
    _atualizar_schema_usuario_legado()
    with SessionLocal() as db:
        criadas = popular_areas(db)
        if criadas:
            logger.info("Áreas iniciais criadas: %s áreas macro.", criadas)
    yield


app = FastAPI(
    title="Chronic Map API",
    description="Trilhas de aprendizado personalizadas com IA.",
    version="1.0.0",
    lifespan=lifespan,
)

_origens = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:8081").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origens,
    allow_credentials=False,  # usamos Bearer token, não cookies
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(areas.router)
app.include_router(diagnostico.router)
app.include_router(trilha.router)
app.include_router(progresso.router)
app.include_router(assistente.router)
app.include_router(usuarios.router)
app.include_router(logs.router)


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}
