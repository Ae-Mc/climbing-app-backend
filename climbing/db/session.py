from sqlite3 import Connection as SQLite3Connection
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from climbing.core.config import settings
from climbing.core.refresh_token.db.database import (
    SQLModelAccessRefreshTokenDatabaseAsync,
)
from climbing.db.models.user import AccessRefreshToken, OAuthAccount, User
from climbing.db.user_database import UserDatabase


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _):
    if (
        isinstance(dbapi_connection, SQLite3Connection)
        or "sqlite" in settings.SQLALCHEMY_DATABASE_URI
    ):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
async_session_maker = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession
    async with async_session_maker() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


async def get_user_db(
    session: AsyncSessionDep,
) -> AsyncGenerator[UserDatabase, None]:
    yield UserDatabase(
        session=session,
        user_model=User,
        oauth_account_model=OAuthAccount,
    )


async def get_access_token_db(
    session: AsyncSessionDep,
) -> AsyncGenerator[SQLModelAccessRefreshTokenDatabaseAsync, None]:
    yield SQLModelAccessRefreshTokenDatabaseAsync(
        access_token_model=AccessRefreshToken,
        session=session,
    )
