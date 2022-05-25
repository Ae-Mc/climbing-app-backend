from typing import Any

from fastapi import HTTPException
from fastapi_users_db_sqlmodel import Field
from pydantic import BaseModel


class ErrorModel(BaseModel):
    """Standard error model"""

    detail: str = Field(title="Описание ошибки")


class ResponseModel:
    """OpenAPI respoonse model"""

    code: int
    description: str = Field(title="Описание ошибки")
    example: ErrorModel = ErrorModel

    def __init__(self, code: int, description: str, model: ErrorModel) -> None:
        self.code = code
        self.description = description
        self.example = model

    def docs(self) -> dict[int | str, dict[str, Any]]:
        """Returns OpenAPI response scheme"""
        return {
            self.code: {
                "description": self.description,
                "model": ErrorModel,
                "content": {
                    "application/json": {"example": self.example.dict()}
                },
            }
        }

    def exception(self) -> HTTPException:
        """Returns FastAPI's HTTPException"""
        return HTTPException(self.code, self.example.detail)


SUPERUSER_REQUIRED = ResponseModel(
    403, "Not a superuser", ErrorModel(detail="You are not a superuser")
)
UNAUTHORIZED = ResponseModel(
    401,
    "Unauthorized",
    ErrorModel(detail="Unauthorized"),
)

ID_NOT_FOUND = ResponseModel(
    404,
    "Item with ID not found",
    ErrorModel(detail="Item with ID not found"),
)
INTEGRITY_ERROR = ResponseModel(
    400,
    "Integrity error occured",
    ErrorModel(detail="Integrity error occured"),
)
