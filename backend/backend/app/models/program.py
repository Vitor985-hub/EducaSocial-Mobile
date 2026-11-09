from dataclasses import dataclass
from enum import StrEnum


class ProgramCategory(StrEnum):
    RENDA = "renda"
    EDUCACAO = "educacao"
    SAUDE = "saude"
    MORADIA = "moradia"
    ALIMENTACAO = "alimentacao"
    TRABALHO = "trabalho"


class CoverageScope(StrEnum):
    NACIONAL = "nacional"
    ESTADUAL = "estadual"
    MUNICIPAL = "municipal"


@dataclass(frozen=True, slots=True)
class Program:
    id: int
    name: str
    summary: str
    description: str
    category: ProgramCategory
    scope: CoverageScope
    state: str | None
    municipality: str | None
    managing_body: str
    eligibility: tuple[str, ...]
    how_to_apply: str
    official_url: str | None
