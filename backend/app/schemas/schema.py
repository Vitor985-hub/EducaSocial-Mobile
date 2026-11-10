from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class OpportunityCreate(BaseModel):
    title: str = Field(min_length=3, max_length=500)
    description: str
    eligibility: str

    required_documents: list[str] = []
    application_steps: list[str] = []

    region_id: int
    category_id: int

    last_reviewed: date
    status: str = "unconfirmed"


class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    eligibility: Optional[str] = None

    required_documents: Optional[list[str]] = None
    application_steps: Optional[list[str]] = None

    region_id: Optional[int] = None
    category_id: Optional[int] = None

    last_reviewed: Optional[date] = None
    status: Optional[str] = None


class OpportunityResponse(BaseModel):
    id: int
    title: str
    description: str
    eligibility: str

    required_documents: list[str]
    application_steps: list[str]

    region_id: int
    category_id: int

    last_reviewed: date
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
