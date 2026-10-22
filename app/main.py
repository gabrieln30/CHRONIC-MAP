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
from app.routers import areas, assistente, auth, diagnostico, progresso, trilha
from app.seed import popular_areas

logger = logging.getLogger("chronic_map")


def _esperar_banco(tentativas: int = 30, intervalo: float = 2.0) -> None:
    """No docker-compose o MySQL demora a aceitar conexões; tentamos por ~1 min."""
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


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}
