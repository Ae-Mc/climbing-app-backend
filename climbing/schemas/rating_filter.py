from pydantic import BaseModel, Field


class RatingFilter(BaseModel):
    is_student: bool | None = Field(None)
