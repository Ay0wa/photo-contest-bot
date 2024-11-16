import os
from dotenv import load_dotenv

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.web.app import Application
from app.store import Store
from app.store import setup_store
from app.database.database import Database

from app.database.base import BaseModel
from app.games.models import GameModel
from app.chats.models import ChatModel
from app.players.models import PlayerModel

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    async_sessionmaker,
)

load_dotenv()

# host = os.getenv("DB_HOST")
# port = os.getenv("DB_PORT")
# user = os.getenv("DB_USER")
# password = os.getenv("DB_PASSWORD")

@pytest.fixture(scope="session")
async def test_db(application: Application, db_engine):
    await application.on_startup()
    
    async with db_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield db_engine

    async with db_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)

    await db_engine.dispose()

@pytest.fixture(scope="session")
def application() -> Application:
    app = Application()
    setup_store(app)
    app.on_startup.clear()
    app.on_shutdown.clear()
    app.on_cleanup.clear()

    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_shutdown.append(app.database.disconnect)

    return app

@pytest.fixture
def db_engine(application: Application) -> AsyncEngine:
    return application.database.engine

@pytest.fixture
async def session(application) -> async_sessionmaker[AsyncSession]:
    return application.database.session

@pytest.fixture
def store(application: Application) -> Store:
    return application.store