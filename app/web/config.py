import os
import typing
from dataclasses import dataclass

from dotenv import load_dotenv

if typing.TYPE_CHECKING:
    from app.web.app import Application

load_dotenv()

# DATABASE SETTINGS
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")


# BOT SETTINGS
token = os.getenv("VK_TOKEN")
group_id = os.getenv("GROUP_ID")


@dataclass
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


@dataclass
class BotConfig:
    token: str
    group_id: int


@dataclass
class Config:
    bot: BotConfig | None = None
    database: DatabaseConfig | None = None


def setup_config(app: "Application"):
    app.config = Config(
        bot=BotConfig(
            token=token,
            group_id=group_id,
        ),
        database=DatabaseConfig(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        ),
    )
