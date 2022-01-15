from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from climbing.db.base_class import Base


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base class for any CRUD classes. Implements default methods for Create,
    Read, Update, Delete (CRUD) operations."""

    model: Type[ModelType]

    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    def get(self, database: Session, row_id: int) -> Optional[ModelType]:
        """Get single row by id

        Args:
            database (Session): database connection
            row_id (int): row id

        Returns:
            Optional[ModelType]: row with id == row_id. Could be None
        """
        return database.get(self.model, row_id)

    def get_all(self, database: Session) -> List[ModelType]:
        """Get all rows

        Args:
            database (Session): database connection

        Returns:
            List[ModelType]: list of rows
        """
        return database.query(self.model).all()

    def create(self, database: Session, entity: CreateSchemaType) -> ModelType:
        """Creates new row in database

        Args:
            database (Session): database connection
            entity (CreateSchemaType): row that will be added

        Returns:
            ModelType:
        """
        entity_data = jsonable_encoder(entity)
        db_entity = self.model(**entity_data)
        database.add(db_entity)
        database.commit()
        database.refresh(db_entity)
        return db_entity

    def update(
        self,
        database: Session,
        *,
        db_entity: ModelType,
        new_entity: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update database row

        Args:
            database (Session): database connection
            db_entity (ModelType): current row value
            new_entity (Union[UpdateSchemaType, Dict[str, Any]]): new row value
                or fields to be updated

        Returns:
            ModelType: updated row value
        """
        entity_data = jsonable_encoder(db_entity)
        if isinstance(new_entity, dict):
            update_data = new_entity
        else:
            update_data = new_entity.dict()
        for field in entity_data:
            if field in update_data:
                setattr(db_entity, field, entity_data[field])
        database.add(db_entity)
        database.commit()
        database.refresh(db_entity)
        return db_entity

    def remove(self, database: Session, *, row_id: int) -> Optional[ModelType]:
        """Removes single row from database

        Args:
            database (Session): database connection
            row_id (int): row id

        Returns:
            None: if row with id == row_id not found
            ModelType: if row successfully removed
        """
        entity = database.get(self.model, row_id)
        database.delete(entity)
        database.commit()
        return entity
