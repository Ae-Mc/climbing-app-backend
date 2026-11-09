"""Regression checks for tourist visibility; run with unittest discover."""

import importlib.util
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel
from starlette.requests import Request

# Import application modules with isolated settings, without real credentials.
with patch.dict(
    "os.environ",
    {
        "SQLALCHEMY_DATABASE_URI": "sqlite+aiosqlite:///:memory:",
        "MAIL_USERNAME": "test",
        "MAIL_SMTP_HOST": "localhost",
        "MAIL_SMTP_PORT": "465",
        "MAIL_EXTERNAL_APP_PASSWORD": "test",
        "MINIO_ACCESS_KEY": "test",
        "MINIO_SECRET_KEY": "test",
        "SECRET": "test",
    },
):
    from climbing.api.api_v2.endpoints.rating import ascents as rating_ascents
    from climbing.api.api_v1.endpoints.routes import router as routes_router
    from climbing.core.security import optional_user
    from climbing.db.session import get_async_session
    from climbing.core.tourist_visibility import rating_tourist_filter
    from climbing.core.user_manager import UserManager
    from climbing.crud.tourist_visibility import (
        visible_ascent_clause,
        visible_route_clause,
    )
    from climbing.db.models import Ascent, Route, User
    from climbing.db.user_database import UserDatabase
    from climbing.schemas.base_read_classes import UserRead
    from climbing.schemas.filters.rating_filter import RatingFilter
    from climbing.util.rating_calculator import RatingCalculator


class TouristVisibilityTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        self.session = AsyncSession(self.engine, expire_on_commit=False)
        self.regular = User(
            username="regular",
            first_name="Test",
            last_name="User",
            email="regular@example.com",
            hashed_password="test",
            sex="male",
        )
        self.tourist = User(
            username="tourist",
            first_name="Test",
            last_name="User",
            email="tourist@example.com",
            hashed_password="test",
            sex="male",
            is_tourist=True,
        )
        self.session.add_all([self.regular, self.tourist])
        await self.session.flush()
        self.routes = [
            Route(
                name=f"Route {i}",
                category="6a",
                mark_color="blue",
                description="",
                creation_date=datetime.now().date(),
                author_id=user.id,
            )
            for i, user in enumerate([self.regular, self.tourist])
        ]
        self.session.add_all(self.routes)
        await self.session.flush()
        self.ascents = [
            Ascent(
                user_id=user.id,
                route_id=route.id,
                date=datetime.now(),
                is_flash=False,
            )
            for user in [self.regular, self.tourist]
            for route in self.routes
        ]
        self.session.add_all(self.ascents)
        await self.session.commit()
        self.request = Request(
            {"type": "http", "scheme": "http", "server": ("test", 80), "path": "/"}
        )
        self.manager = UserManager(UserDatabase(self.session, User))

    async def asyncTearDown(self):
        await self.session.close()
        await self.engine.dispose()

    async def test_visibility_matrix(self):
        for viewer, expected_routes, expected_ascents in [
            (None, 1, 1),
            (self.regular, 1, 1),
            (self.tourist, 2, 4),
        ]:
            include = viewer is not None and viewer.is_tourist
            routes = (
                (
                    await self.session.execute(
                        select(Route).where(visible_route_clause(include))
                    )
                )
                .scalars()
                .all()
            )
            ascents = (
                (
                    await self.session.execute(
                        select(Ascent).where(visible_ascent_clause(include))
                    )
                )
                .scalars()
                .all()
            )
            self.assertEqual(len(routes), expected_routes)
            self.assertEqual(len(ascents), expected_ascents)
            for only_tourists in [False, True]:
                expected = (True if only_tourists else None) if include else False
                self.assertIs(
                    rating_tourist_filter(viewer, only_tourists), expected
                )

    async def test_route_http_visibility(self):
        app = FastAPI()
        app.include_router(routes_router, prefix="/routes")

        async def session_override():
            yield self.session

        app.dependency_overrides[get_async_session] = session_override
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            for viewer in [None, self.regular, self.tourist]:
                app.dependency_overrides[optional_user] = lambda: viewer
                listing = await client.get("/routes")
                self.assertEqual(listing.status_code, 200)
                self.assertEqual(
                    len(listing.json()), 2 if viewer is self.tourist else 1
                )
                detail = await client.get(f"/routes/{self.routes[1].id}")
                self.assertEqual(
                    detail.status_code, 200 if viewer is self.tourist else 404
                )

    async def test_rating_modes(self):
        for mode, expected_users, expected_ascents in [
            (False, {self.regular.id}, 1),
            (True, {self.tourist.id}, 2),
            (None, {self.regular.id, self.tourist.id}, 2),
        ]:
            calc = RatingCalculator(self.session, RatingFilter(is_tourist=mode))
            await calc.calc_routes_competition(self.request)
            calc.fill_routes_competition_scores()
            await calc.fill_ascents(self.request)
            self.assertEqual({s.user.id for s in calc.scores}, expected_users)
            for score in calc.scores:
                self.assertEqual(len(score.ascents), expected_ascents)
                if mode is False:
                    self.assertEqual(score.ascents[0].route.id, self.routes[0].id)

    async def test_v2_hides_tourist_routes(self):
        for viewer, count in [(None, 1), (self.regular, 1), (self.tourist, 2)]:
            result = await rating_ascents(
                request=self.request,
                session=self.session,
                start_date=None,
                end_date=None,
                user_id=self.regular.id,
                viewer=viewer,
                user_manager=self.manager,
            )
            self.assertEqual(len(result), count)
            if count == 1:
                self.assertEqual(result[0].route.id, self.routes[0].id)

    async def test_v2_missing_and_hidden_users_share_error(self):
        for user_id in [uuid4(), self.tourist.id]:
            with self.assertRaises(HTTPException) as error:
                await rating_ascents(
                    request=self.request,
                    session=self.session,
                    start_date=None,
                    end_date=None,
                    user_id=user_id,
                    viewer=None,
                    user_manager=self.manager,
                )
            self.assertEqual(error.exception.status_code, 404)
            self.assertEqual(error.exception.detail, "Item with ID not found")

    async def test_tourist_status_persists_and_is_inherited_by_read_schema(self):
        for value in [True, False]:
            updated = await self.manager.set_tourist_status(self.regular, value)
            self.assertIs(UserRead.model_validate(updated).is_tourist, value)
            await self.session.refresh(self.regular)
            self.assertIs(self.regular.is_tourist, value)


class TouristMigrationTests(unittest.TestCase):
    def test_upgrade_existing_users_and_downgrade(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "alembic/versions/62c5e0a9b441_add_is_tourist_to_user.py"
        )
        spec = importlib.util.spec_from_file_location("tourist_migration", path)
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        engine = create_engine("sqlite:///:memory:")
        with engine.begin() as connection:
            connection.execute(text("CREATE TABLE user (id INTEGER PRIMARY KEY)"))
            connection.execute(text("INSERT INTO user (id) VALUES (1)"))
            with Operations.context(MigrationContext.configure(connection)):
                migration.upgrade()
                self.assertEqual(
                    connection.scalar(
                        text("SELECT is_tourist FROM user WHERE id = 1")
                    ),
                    0,
                )
                connection.execute(text("INSERT INTO user (id) VALUES (2)"))
                self.assertEqual(
                    connection.scalar(
                        text("SELECT is_tourist FROM user WHERE id = 2")
                    ),
                    0,
                )
                migration.downgrade()
                self.assertEqual(
                    connection.scalar(text("SELECT count(*) FROM user")), 2
                )
                self.assertNotIn(
                    "is_tourist",
                    [
                        row[1]
                        for row in connection.execute(
                            text("PRAGMA table_info(user)")
                        )
                    ],
                )
        engine.dispose()
