from datetime import datetime
from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import (
    SQLAlchemyBaseOAuthAccountTable,
    SQLAlchemyBaseUserTable,
)
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyBaseAccessTokenTable,
)
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declared_attr, relationship

from climbing.db.base_class import Base

if TYPE_CHECKING:
    from climbing.models.route import Route


class User(Base, SQLAlchemyBaseUserTable):
    """Table for storing users"""

    @declared_attr
    def __tablename__(self) -> str:
        return SQLAlchemyBaseUserTable.__tablename__

    username = Column(
        String(length=50), unique=True, index=True, nullable=False
    )
    first_name = Column(String(length=100), nullable=False)
    last_name = Column(String(length=100), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    routes: "Route" = relationship("Route", back_populates="uploader")
    oauth_accounts = relationship("OAuthAccount")


class OAuthAccount(Base, SQLAlchemyBaseOAuthAccountTable):
    """Table for storing OAuth accounts for each user"""

    @declared_attr
    def __tablename__(self) -> str:
        return SQLAlchemyBaseOAuthAccountTable.__tablename__


class AccessToken(Base, SQLAlchemyBaseAccessTokenTable):
    """Table for storing access tokens"""
