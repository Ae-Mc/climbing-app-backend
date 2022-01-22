from pydantic import BaseModel, Field


class Image(BaseModel):
    """Модель для хранения изображений."""

    url: str = Field(..., title="URL-адрес изображения")

    # pylint: disable=too-few-public-methods,missing-class-docstring
    class Config:
        orm_mode = True
