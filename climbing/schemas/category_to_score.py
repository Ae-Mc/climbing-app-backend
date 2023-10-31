from pydantic import BaseModel, Field

from climbing.db.models.category import Category


class CategoryToScore(BaseModel):
    """Модель для описания цены категории"""

    category: Category = Field(..., title="Категория")
    score: float = Field(..., title="Количество очков за прохождение")
