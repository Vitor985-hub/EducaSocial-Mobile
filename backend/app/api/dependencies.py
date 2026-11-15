import logging
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.ai.core.exceptions import AIServiceError
from app.core.config import get_settings
from app.integrations.ai_client import AIServiceClient, DisabledAIClient, InProcessAIClient
from app.repositories.fake_programs import FAKE_PROGRAMS
from app.repositories.in_memory_program import InMemoryProgramRepository
from app.repositories.program import ProgramRepository
from app.services.assistant_service import AssistantService
from app.services.program_service import ProgramService

logger = logging.getLogger(__name__)


@lru_cache
def get_program_repository() -> ProgramRepository:
    return InMemoryProgramRepository(FAKE_PROGRAMS)


def get_program_service(
    repository: Annotated[ProgramRepository, Depends(get_program_repository)],
) -> ProgramService:
    return ProgramService(repository)


@lru_cache
def get_ai_client() -> AIServiceClient:
    if not get_settings().ai_enabled:
        return DisabledAIClient()
    from app.ai.container import build_rag_service
    from app.ai.core.config import get_settings as get_ai_settings
    from app.database import engine

    try:
        return InProcessAIClient(build_rag_service(get_ai_settings(), engine))
    except AIServiceError as exc:
        logger.error("Módulo de IA não pôde ser iniciado (%s): %s", exc.code, exc.message)
        return DisabledAIClient()


def get_assistant_service(
    client: Annotated[AIServiceClient, Depends(get_ai_client)],
) -> AssistantService:
    return AssistantService(client)


ProgramServiceDep = Annotated[ProgramService, Depends(get_program_service)]
AssistantServiceDep = Annotated[AssistantService, Depends(get_assistant_service)]
