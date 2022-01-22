from typing import Any, Dict, Type, Union, cast
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from climbing.api.deps import FileStorage
from climbing.core.config import settings
from climbing.models import File, Route, RouteImage
from climbing.schemas.route import RouteCreate, RouteUpdate

from .base import CRUDBase


class CRUDRoute(CRUDBase[Route, RouteCreate, RouteUpdate]):
    """CRUD class for route models"""

    def __init__(self, model: Type[Route] = Route) -> None:
        super().__init__(model)

    async def get(self, session: AsyncSession, row_id: UUID) -> Route | None:
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
        files: list[File] = []
        for file in entity.images:
            image_path = storage.save(file)
            files.append(
                File(  # type: ignore
                    url=image_path, uploader_id=entity.uploader.id
                )
            )
            session.add(files[-1])
        entity_data = entity.dict(exclude={"images": True, "uploader": True})
        db_route = self.model(  # type: ignore
            **entity_data,
            uploader_id=entity.uploader.id,
        )
        session.add(db_route)
        await session.commit()
        await session.refresh(db_route)
        for file in files:
            await session.refresh(file)
            session.add(RouteImage(route_id=db_route.id, image_id=file.id))  # type: ignore
        await session.commit()
        await session.refresh(db_route)
        route_instance = await self.get(session, cast(UUID, db_route.id))
        if route_instance is None:
            raise IndexError("Can't find created route")
        return route_instance

    async def update(
        self,
        session: AsyncSession,
        *,
        db_entity: Route,
        new_entity: Union[RouteUpdate, Dict[str, Any]],
    ) -> Route:
        print(f"Old: {db_entity}\nNew: {new_entity}")

    async def remove(self, session: AsyncSession, *, row_id: UUID) -> None:
        route_instance = (
            await session.execute(select(Route).where(Route.id == row_id))
        ).scalar_one_or_none()
        if route_instance is None:
            return
        route_images = (
            (
                await session.execute(
                    select(RouteImage).where(RouteImage.route_id == row_id)
                )
            )
            .scalars()
            .all()
        )
        files: list[File] = (
            (
                await session.execute(
                    select(File).where(
                        File.id.in_(
                            list(map(lambda x: x.image_id, route_images))
                        )
                    )
                )
            )
            .scalars()
            .all()
        )
        for image in route_images:
            await session.delete(image)
        storage = FileStorage(settings.MEDIA_ROOT)
        for file in files:
            storage.remove(file.url)  # type: ignore
            await session.delete(file)
        await session.delete(route_instance)
        await session.commit()


route = CRUDRoute(Route)
