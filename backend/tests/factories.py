from dataclasses import replace
from typing import Any

from app.models.program import CoverageScope, Program, ProgramCategory

_BASE = Program(
    id=1,
    name="Programa de teste",
    summary="Resumo de teste.",
    description="Descrição de teste.",
    category=ProgramCategory.RENDA,
    scope=CoverageScope.NACIONAL,
    state=None,
    municipality=None,
    managing_body="Órgão de teste",
    eligibility=("Critério de teste.",),
    how_to_apply="Como solicitar, em teste.",
    official_url=None,
)


def make_program(**overrides: Any) -> Program:
    return replace(_BASE, **overrides)
