from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users_db_sqlmodel.access_token import (
    SQLModelAccessTokenDatabaseAsync,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from climbing.core.config import settings
from climbing.db.models.user import AccessToken, OAuthAccount, User
from climbing.db.user_database import UserDatabase

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
async_session_maker = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[UserDatabase, None]:
    yield UserDatabase(User, session, OAuthAccount)


async def get_access_token_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLModelAccessTokenDatabaseAsync, None]:
    yield SQLModelAccessTokenDatabaseAsync(AccessToken, session)
