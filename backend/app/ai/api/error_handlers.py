from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.ai.core.exceptions import AIServiceError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AIServiceError)
    async def handle_service_error(request: Request, exc: AIServiceError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )
