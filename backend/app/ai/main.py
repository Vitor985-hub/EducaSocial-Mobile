from fastapi import FastAPI

from app.ai.api.error_handlers import register_exception_handlers
from app.ai.api.routes import health, query


def create_app() -> FastAPI:
    app = FastAPI(
        title="Educa Social — Módulo de IA",
        version="0.1.0",
        description="Serviço RAG que responde perguntas com base em fontes oficiais.",
    )
    register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(query.router)
    return app


app = create_app()
