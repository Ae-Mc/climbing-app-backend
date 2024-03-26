from typing import Any, Callable, Generic, Sequence, Type, TypeVar
from uuid import UUID

from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.selectable import Select
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base class for any CRUD classes. Implements default methods for Create,
    Read, Update, Delete (CRUD) operations."""

    model: Type[ModelType]
    select_options: list = [selectinload("*")]

    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    async def get(self, session: AsyncSession, row_id: UUID4) -> ModelType | None:
        """Get single row by id

        Args:
            session (Session): database connection
            row_id (UUID4): row id

        Returns:
            ModelType | None: row with id == row_id. Could be None
        """
        return (
            await session.execute(
                select(self.model)
                .where(self.model.id == row_id)
                .options(*self.select_options)
            )
        ).scalar_one_or_none()

    async def get_all(
        self,
        session: AsyncSession,
        query_modifier: Callable[[Select], Select] | None = None,
    ) -> Sequence[ModelType]:
        """Get all rows

        Args:
            session (Session): database connection

        Returns:
            list[ModelType]: list of rows
        """
        query: Select[tuple[ModelType]] = select(self.model).options(
            *self.select_options
        )
        if query_modifier is not None:
            query = query_modifier(query)

        return (await session.execute(query)).scalars().all()

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
        entity_data = entity.model_dump()
        db_entity = self.model(**entity_data)  # type: ignore
        session.add(db_entity)
        await session.commit()
        result = await self.get(session, db_entity.id)
        assert result is not None
        return result

    async def update(
        self,
        session: AsyncSession,
        *,
        db_entity: ModelType,
        new_entity: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """Update database row

        Args:
            session (Session): database connection
            db_entity (ModelType): current row value
            new_entity (UpdateSchemaType | dict[str, Any]): new row value
                or fields to be updated

        Returns:
            ModelType: updated row value
        """
        if isinstance(new_entity, dict):
            update_data = new_entity
        else:
            update_data = new_entity.model_dump(exclude_unset=True)
        db_entity.sqlmodel_update(update_data)
        session.add(db_entity)
        await session.commit()
        await session.refresh(db_entity)
        ident = getattr(db_entity, "id", None)
        if ident is None or not isinstance(ident, UUID):
            print(f"No ident: {ident}, (for entity of type {self.model})")
            return db_entity
        else:
            result = await self.get(session, ident)
            assert result is not None
            return result

    async def remove(self, session: AsyncSession, *, row_id: UUID4) -> ModelType | None:
        """Removes single row from database

        Args:
            session (Session): database connection
            row_id (UUID4): row id

        Returns:
            None: if row with id == row_id not found
            ModelType: if row successfully removed
        """
        entity = await session.get(self.model, row_id)
        if entity is not None:
            await session.delete(entity)
            await session.commit()
        return entity
