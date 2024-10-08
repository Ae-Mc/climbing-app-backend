from datetime import timedelta

from pydantic import validator
from pydantic_settings import BaseSettings


# pylint: disable=too-few-public-methods
class Settings(BaseSettings):
    """Class for storing app settings"""

    ACCESS_TOKEN_EXPIRE_TIME: timedelta = timedelta(days=180)
    REFRESH_TOKEN_EXPIRE_TIME: timedelta = timedelta(days=180)
    SQLALCHEMY_DATABASE_URI: str | None = None
    AUTH_TOKEN_ENDPOINT_URL: str = "/api/v2/auth/login"
    MEDIA_ROOT: str = "media"
    MAIL_USERNAME: str
    MAIL_SMTP_HOST: str
    MAIL_SMTP_PORT: int
    MAIL_EXTERNAL_APP_PASSWORD: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_HOST: str = "files.ae-mc.ru"
    MINIO_BUCKET_NAME: str = "climbing"
    SECRET: str

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


settings = Settings()  # type: ignore
