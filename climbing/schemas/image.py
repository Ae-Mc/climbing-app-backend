from pydantic import BaseModel, Field, HttpUrl


class Image(BaseModel):
    """Модель для хранения изображений."""

    url: HttpUrl = Field(..., title="URL-адрес изображения")
