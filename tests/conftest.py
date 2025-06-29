import logging
from asyncio import AbstractEventLoop
from collections.abc import Iterator

import pytest
from aiohttp.pytest_plugin import AiohttpClient
from aiohttp.test_utils import TestClient, loop_context
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from alembic import command
from alembic.config import Config
from app.database.database import Database
from app.store.store import Store
from app.web.app import Application, setup_app


@pytest.fixture(scope="session", autouse=True)
def apply_migrations(application: Application):
    alembic_cfg = Config("alembic.ini")

    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session")
def event_loop() -> Iterator[None]:
    with loop_context() as _loop:
        yield _loop


@pytest.fixture(scope="session")
def application() -> Application:
    app = setup_app()

    app.on_startup.clear()
    app.on_shutdown.clear()
    app.on_cleanup.clear()

    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_shutdown.append(app.database.disconnect)

    return app


@pytest.fixture
def store(application: Application) -> Store:
    return application.store


@pytest.fixture
def db_sessionmaker(
    application: Application,
) -> async_sessionmaker[AsyncSession]:
    return application.database.session


@pytest.fixture
def db_engine(application: Application) -> AsyncEngine:
    return application.database.engine


@pytest.fixture
async def inspect_list_tables(db_engine: AsyncEngine) -> list[str]:
    def use_inspector(connection: AsyncConnection) -> list[str]:
        inspector = inspect(connection)
        return inspector.get_table_names()

    async with db_engine.begin() as conn:
        return await conn.run_sync(use_inspector)


@pytest.fixture(autouse=True)
async def clear_db(application: Application) -> Iterator[None]:
    try:
        yield
    except Exception:
        logging.warning("Ошибка при тестировании")
    finally:
        async_session = AsyncSession(application.database.engine)
        async with async_session.begin():
            connection = await async_session.connection()

            for table in application.database._db.metadata.tables.values():
                await connection.execute(text(f"TRUNCATE {table} CASCADE"))
                await connection.execute(
                    text(f"ALTER SEQUENCE {table}_id_seq RESTART WITH 1"),
                )
            enum_types = await connection.execute(
                text("""
                SELECT typname
                FROM pg_type
                WHERE typcategory = 'E';
            """)
            )
            enum_types = enum_types.fetchall()

            for enum in enum_types:
                enum_name = enum[0]
                await connection.execute(
                    text(f"DROP TYPE IF EXISTS {enum_name} CASCADE")
                )

        await async_session.close()


@pytest.fixture
def config(application: Application):
    return application.config


@pytest.fixture(autouse=True)
def cli(
    aiohttp_client: AiohttpClient,
    event_loop: AbstractEventLoop,
    application: Application,
) -> TestClient:
    return event_loop.run_until_complete(aiohttp_client(application))
