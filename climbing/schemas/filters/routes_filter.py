from pydantic import UUID4, BaseModel, Field


class RoutesFilter(BaseModel):
    archived: bool | None = Field(None)
    author_id: UUID4 | None = Field(None)
