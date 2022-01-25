from typing import Any, Type

from fastapi_users_db_sqlalchemy import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from climbing.api.deps import FileStorage
from climbing.core.config import settings
from climbing.db.models import Route, RouteCreate, RouteImage, RouteUpdate

from .base import CRUDBase


class CRUDRoute(CRUDBase[Route, RouteCreate, RouteUpdate]):
    """CRUD class for route models"""

    def __init__(self, model: Type[Route] = Route) -> None:
        super().__init__(model)

    async def get(self, session: AsyncSession, row_id: UUID4) -> Route | None:
        return (
            await session.execute(
                select(Route)
                .options(selectinload("images"))
                .options(selectinload("uploader"))
                .where(Route.id == row_id)
            )
        ).scalar_one_or_none()

    async def get_all(self, session: AsyncSession) -> list[Route]:
        return (
            (
                await session.execute(
                    select(self.model)
                    .options(selectinload("images"))
                    .options(selectinload("uploader"))
                )
            )
            .scalars()
            .all()
        )

    async def create(
        self, session: AsyncSession, entity: RouteCreate
    ) -> Route:
        storage = FileStorage(settings.MEDIA_ROOT)
        images: list[RouteImage] = []
        entity_data = entity.dict(exclude={"images": True, "uploader": True})
        route_instance = self.model(
            **entity_data,
            uploader_id=entity.uploader.id,
        )
        session.add(route_instance)
        await session.refresh(route_instance)
        for image in entity.images:
            image_path = storage.save(image)
            images.append(
                RouteImage(
                    url=image_path,
                    uploader_id=entity.uploader.id,
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

    async def update(
        self,
        session: AsyncSession,
        *,
        db_entity: Route,
        new_entity: RouteUpdate | dict[str, Any],
    ) -> Route:
        print(f"Old: {db_entity}\nNew: {new_entity}")

    async def remove(self, session: AsyncSession, *, row_id: UUID4) -> None:
        route_instance: Route | None = (
            await session.execute(
                select(Route)
                .where(Route.id == row_id)
                .options(selectinload("images"))
            )
        ).scalar_one_or_none()
        if route_instance is None:
            return
        images: list[RouteImage] = route_instance.images
        for image in images:
            await session.delete(image)
        storage = FileStorage(settings.MEDIA_ROOT)
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


route = CRUDRoute(Route)
