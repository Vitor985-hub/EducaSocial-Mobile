from fastapi import APIRouter

from app.api.routes import assistant, programs

api_router = APIRouter()
api_router.include_router(programs.router)
api_router.include_router(assistant.router)
