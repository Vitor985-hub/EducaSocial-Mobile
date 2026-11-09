from pydantic import BaseModel, ConfigDict, Field


class AIQueryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=3, max_length=1000)
    state: str | None = Field(default=None, min_length=2, max_length=2)
    municipality: str | None = Field(default=None, min_length=2, max_length=100)


class AISource(BaseModel):
    title: str
    program_id: int | None = None
    url: str | None = None


class AIQueryResponse(BaseModel):
    answer: str
    sources: list[AISource] = Field(default_factory=list)
