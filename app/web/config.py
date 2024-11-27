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


# SESSION SETTINGS
key = os.getenv("SECRET_KEY")


# ADMIN SETTINGS
email = os.getenv("EMAIL")
admin_password = os.getenv("ADMIN_PASSWORD")


@dataclass
class SessionConfig:
    key: str


@dataclass
class AdminConfig:
    email: str
    password: str


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
    session: SessionConfig | None = None
    admin: AdminConfig | None = None
    bot: BotConfig | None = None
    database: DatabaseConfig | None = None


def setup_config(app: "Application"):
    app.config = Config(
        session=SessionConfig(
            key=key,
        ),
        admin=AdminConfig(
            email=email,
            password=admin_password,
        ),
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
