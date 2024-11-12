import json
import os
import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from app.web.app import Application

CONFIG_PATH = os.getenv("CONFIGPATH")


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


def load_config():
    with open(CONFIG_PATH, "r") as config_file:
        return json.load(config_file)


def setup_config(app: "Application"):
    raw_config = load_config()

    app.config = Config(
        bot=BotConfig(
            token=raw_config["bot"]["token"],
            group_id=raw_config["bot"]["group_id"],
        ),
        database=DatabaseConfig(**raw_config["database"]),
    )
