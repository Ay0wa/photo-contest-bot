from aiohttp.web import Application as AiohttpApplication

from app.database.database import Database
from app.store.store import Store, setup_store

from .config import Config, setup_config
from .routes import setup_routes

__all__ = ("Application",)


class Application(AiohttpApplication):
    config: Config | None = None
    store: Store | None = None
    database: Database | None = None


app = Application()


def setup_app() -> Application:
    setup_config(app)
    setup_store(app)
    setup_routes(app)
    return app
