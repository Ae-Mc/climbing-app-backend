from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

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

    async def get(
        self, database: AsyncSession, row_id: UUID
    ) -> ModelType | None:
        """Get single row by id

        Args:
            database (Session): database connection
            row_id (UUID): row id

        Returns:
            ModelType | None: row with id == row_id. Could be None
        """
        return await database.get(self.model, row_id, options=[selectinload])

    async def get_all(self, session: AsyncSession) -> list[ModelType]:
        """Get all rows

        Args:
            session (Session): database connection

        Returns:
            list[ModelType]: list of rows
        """
        return (await session.execute(select(self.model))).scalars().all()

    async def create(
        self, session: AsyncSession, entity: CreateSchemaType
    ) -> ModelType:
        """Creates new row in database

        Args:
            session (Session): database connection
            entity (CreateSchemaType): row that will be added

        Returns:
            ModelType:
        """
        entity_data = jsonable_encoder(entity)
        db_entity = self.model(**entity_data)  # type: ignore
        session.add(db_entity)
        await session.commit()
        await session.refresh(db_entity)
        return db_entity

    async def update(
        self,
        database: AsyncSession,
        *,
        db_entity: ModelType,
        new_entity: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """Update database row

        Args:
            database (Session): database connection
            db_entity (ModelType): current row value
            new_entity (UpdateSchemaType | dict[str, Any]): new row value
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
        await database.commit()
        await database.refresh(db_entity)
        return db_entity

    async def remove(
        self, database: AsyncSession, *, row_id: UUID
    ) -> ModelType | None:
        """Removes single row from database

        Args:
            database (Session): database connection
            row_id (UUID): row id

        Returns:
            None: if row with id == row_id not found
            ModelType: if row successfully removed
        """
        entity = await database.get(self.model, row_id)
        await database.delete(entity)
        await database.commit()
        return entity
