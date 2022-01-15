from datetime import timedelta
from typing import Optional

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Class for storing app settings"""

    ACCESS_TOKEN_EXPIRE_TIME = timedelta(hours=1)
    API_V1_STR: str = "/api/v1"
    SQLALCHEMY_DATABASE_URI: str = None
    AUTH_TOKEN_ENDPOINT_URL: str = "auth/login"

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    @classmethod
    def assemble_sqlalchemy_database_uri(cls, value: Optional[str]) -> str:
        """Sets value of attribute SQLALCHEMY_DATABASE_URI

        Args:
            value (Optional[str]): current value of attribute

        Returns:
            str: new value of attribute
        """
        if isinstance(value, str):
            return value
        return "sqlite+aiosqlite:///climbing.db"


settings = Settings()
