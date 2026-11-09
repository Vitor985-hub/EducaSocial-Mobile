from pydantic import BaseModel, ConfigDict

from app.models.program import CoverageScope, ProgramCategory


class ProgramSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    summary: str
    category: ProgramCategory
    scope: CoverageScope
    state: str | None
    municipality: str | None


class ProgramDetail(ProgramSummary):
    description: str
    managing_body: str
    eligibility: list[str]
    how_to_apply: str
    official_url: str | None
