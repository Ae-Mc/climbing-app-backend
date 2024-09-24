from typing import Any, Sequence

from fastapi import UploadFile
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from climbing.api.deps import FileStorage
from climbing.db.models import Route, RouteCreate, RouteImage, RouteUpdate

from .base import CRUDBase


class CRUDRoute(CRUDBase[Route, RouteCreate, RouteUpdate]):
    """CRUD class for route models"""

    async def get_for_user(
        self, session: AsyncSession, user_id: UUID4
    ) -> Sequence[Route]:
        """Получение списка трасс для пользователя"""

        return (
            (
                await session.execute(
                    select(self.model)
                    .options(*self.select_options)
                    .where(self.model.author_id == user_id)
                )
            )
            .scalars()
            .all()
        )

    async def update(
        self,
        session: AsyncSession,
        *,
        db_entity: Route,
        new_entity: RouteUpdate | dict[str, Any],
    ) -> Route:
        if isinstance(new_entity, RouteUpdate):
            update_data = new_entity.model_dump(exclude={"images": True})
            images = new_entity.images
        elif isinstance(new_entity, dict):
            update_data = new_entity
            images: list[UploadFile] = update_data.pop("images", None)
        db_entity = await super().update(
            session, db_entity=db_entity, new_entity=update_data
        )
        storage = FileStorage()
        for image in db_entity.images:
            await session.delete(image)
            if storage.exists(image.url):
                storage.remove(image.url)
        db_entity.images.clear()

        for image in images:
            db_entity.images.append(
                RouteImage(
                    url=storage.save(image, prefix="routes_images/"),
                    route_id=db_entity.id,
                )
            )
        session.add(db_entity)
        await session.commit()
        result = await self.get(session, db_entity.id)
        assert result is not None
        return result

    async def create(self, session: AsyncSession, entity: RouteCreate) -> Route:
        storage = FileStorage()
        images: list[RouteImage] = []
        entity_data = entity.model_dump(exclude={"images": True, "author": True})
        route_instance = self.model(**entity_data)
        session.add(route_instance)
        await session.commit()
        await session.refresh(route_instance, attribute_names={"id"})
        for image in entity.images:
            images.append(
                RouteImage(
                    url=storage.save(image, prefix="routes_images/"),
                    route_id=route_instance.id,
                )
            )
            session.add(images[-1])
        await session.commit()
        route_instance = await self.get(session, route_instance.id)
        if route_instance is None:
            for image in images:
                storage.remove(image.url)
            raise IndexError("Can't find created route")
        return route_instance

    async def remove(self, session: AsyncSession, *, row_id: UUID4) -> None:
        route_instance = await self.get(session, row_id)
        if route_instance is None:
            return
        images = route_instance.images
        for image in images:
            await session.delete(image)
        storage = FileStorage()
        for image in images:
            try:
                storage.remove(image.url)
            except FileNotFoundError:
                print(
                    f"File {image.url} associated with"
                    f" route {route_instance.name} (id={route_instance.id})"
                    f" not found"
                )
        await session.delete(route_instance)
        await session.commit()

    async def archive(
        self, session: AsyncSession, *, row_id: UUID4, archived: bool = True
    ) -> Route | None:
        route = await self.get(session, row_id)
        if route is None:
            return route
        route.archived = archived
        session.add(route)
        await session.commit()
        return route


route = CRUDRoute(Route)
