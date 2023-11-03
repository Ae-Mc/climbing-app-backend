from pydantic import BaseModel, Field

from climbing.db.models.user import SexEnum


class RatingFilter(BaseModel):
    is_student: bool | None = Field(None)
    sex: SexEnum | None = Field(None)
