import os
from datetime import timedelta

from pydantic import validator
from pydantic_settings import BaseSettings


# pylint: disable=too-few-public-methods
class Settings(BaseSettings):
    """Class for storing app settings"""

    ACCESS_TOKEN_EXPIRE_TIME: timedelta = timedelta(hours=1)
    REFRESH_TOKEN_EXPIRE_TIME: timedelta = timedelta(days=180)
    API_V1_STR: str = "/api/v1"
    SQLALCHEMY_DATABASE_URI: str | None = None
    AUTH_TOKEN_ENDPOINT_URL: str = f"{API_V1_STR}/auth/login"
    MEDIA_ROOT: str = "media"
    MAIL_USERNAME: str = os.getenv("MAIL_PASSWORD")  # type: ignore
    MAIL_SMTP_HOST: str = os.getenv("MAIL_SMTP_HOST")  # type: ignore
    MAIL_SMTP_PORT: int = int(os.getenv("MAIL_SMTP_PORT"))  # type: ignore
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")  # type: ignore
    SECRET: str = os.getenv("SECRET")  # type: ignore

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    @classmethod
    def assemble_sqlalchemy_database_uri(cls, value: str | None) -> str:
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
