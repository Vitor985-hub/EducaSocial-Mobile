from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class QueryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=3, max_length=1000)
    state: str | None = Field(default=None, min_length=2, max_length=2)
    municipality: str | None = Field(default=None, min_length=2, max_length=100)

    @field_validator("state")
    @classmethod
    def uppercase_state(cls, value: str | None) -> str | None:
        return value.upper() if value else value

    @model_validator(mode="after")
    def municipality_requires_state(self) -> "QueryRequest":
        if self.municipality and not self.state:
            raise ValueError("municipality exige state.")
        return self


class Source(BaseModel):
    title: str
    program_id: int | None = None
    url: str | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source] = Field(default_factory=list)
