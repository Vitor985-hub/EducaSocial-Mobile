from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.integrations.ai_client import AIServiceClient, DisabledAIClient
from app.repositories.fake_programs import FAKE_PROGRAMS
from app.repositories.in_memory_program import InMemoryProgramRepository
from app.repositories.program import ProgramRepository
from app.services.assistant_service import AssistantService
from app.services.program_service import ProgramService


@lru_cache
def get_program_repository() -> ProgramRepository:
    return InMemoryProgramRepository(FAKE_PROGRAMS)


def get_program_service(
    repository: Annotated[ProgramRepository, Depends(get_program_repository)],
) -> ProgramService:
    return ProgramService(repository)


def get_ai_client() -> AIServiceClient:
    return DisabledAIClient()


def get_assistant_service(
    client: Annotated[AIServiceClient, Depends(get_ai_client)],
) -> AssistantService:
    return AssistantService(client)


ProgramServiceDep = Annotated[ProgramService, Depends(get_program_service)]
AssistantServiceDep = Annotated[AssistantService, Depends(get_assistant_service)]
