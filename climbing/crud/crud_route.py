from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from climbing.api.deps import FileStorage
from climbing.core.config import settings
from climbing.db.models import Route, RouteCreate, RouteImage, RouteUpdate

from .base import CRUDBase


class CRUDRoute(CRUDBase[Route, RouteCreate, RouteUpdate]):
    """CRUD class for route models"""

    select_options = (selectinload(Route.images), selectinload(Route.author))

    async def get_for_user(
        self, session: AsyncSession, user_id: UUID4
    ) -> list[Route]:
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

    async def create(
        self, session: AsyncSession, entity: RouteCreate
    ) -> Route:
        storage = FileStorage(settings.MEDIA_ROOT)
        images: list[RouteImage] = []
        entity_data = entity.dict(exclude={"images": True, "author": True})
        route_instance = self.model(**entity_data, author_id=entity.author.id)
        session.add(route_instance)
        await session.commit()
        await session.refresh(route_instance, attribute_names={"id"})
        for image in entity.images:
            images.append(
                RouteImage(url=storage.save(image), route=route_instance)
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
