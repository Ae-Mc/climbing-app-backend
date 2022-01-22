from pydantic import BaseModel, Field


class File(BaseModel):
    url: str = Field(...)
