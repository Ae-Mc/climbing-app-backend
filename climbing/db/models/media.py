from datetime import datetime, timezone
from uuid import uuid4

from pydantic import UUID4
from sqlmodel import Field, SQLModel


class Media(SQLModel):
    id: UUID4 = Field(default_factory=uuid4, primary_key=True)
    s3_object_name: str = Field()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
