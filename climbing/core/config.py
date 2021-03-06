from datetime import timedelta

from pydantic import BaseSettings, validator


# pylint: disable=too-few-public-methods
class Settings(BaseSettings):
    """Class for storing app settings"""

    ACCESS_TOKEN_EXPIRE_TIME = timedelta(hours=1)
    API_V1_STR: str = "/api/v1"
    SQLALCHEMY_DATABASE_URI: str | None = None
    AUTH_TOKEN_ENDPOINT_URL: str = f"{API_V1_STR}/auth/login"
    MEDIA_ROOT: str = "media"

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
