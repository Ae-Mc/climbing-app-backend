from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session
from core.security import get_password_hash, verify_password
from crud.base import CRUDBase
from models.user import User
from schemas import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """User model's CRUD class"""

    def get_by_username(
        self, database: Session, username: str
    ) -> Optional[User]:
        return database.query(User).filter(User.username == username).first()

    def create(self, database: Session, entity: UserCreate) -> User:
        """Creates new user

        Args:
            database (Session): database connection
            entity (UserCreate): user parameters

        Returns:
            [User]: created user
        """

        hashed_password = get_password_hash(entity.password.get_secret_value())
        entity_dict = entity.dict()
        del entity_dict["password"]
        db_user = User(**entity_dict, hashed_password=hashed_password)
        database.add(db_user)
        database.commit()
        database.refresh(db_user)
        return db_user

    def update(
        self,
        database: Session,
        *,
        db_entity: User,
        new_entity: Union[UserUpdate, Dict[str, Any]]
    ):
        if isinstance(new_entity, dict):
            update_data = new_entity
        else:
            update_data = new_entity.dict()
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data["password"]
            )
            del update_data["password"]
        return super().update(
            database=database, db_entity=db_entity, new_entity=update_data
        )

    def authorize(
        self, database: Session, username: str, password: str
    ) -> Optional[User]:
        """Authorizes user

        Args:
            database (Session): database connection
            username (str): user's username
            password (str): user's password

        Returns:
            Optional[User]: user if successfully authorized else None
        """
        usr: User = (
            database.query(User).filter(User.username == username).first()
        )
        if usr is None or not verify_password(password, usr.hashed_password):
            return None
        return usr


user = CRUDUser(User)
