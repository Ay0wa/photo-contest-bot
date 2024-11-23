import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.database.database import Database


class Store:
    def __init__(self, app: "Application", *args, **kwargs):
        from app.bot.manager import BotManager
        from app.chats.accessor import ChatAccesor
        from app.games.accessor import GameAccesor
        from app.players.accessor import PlayerAccesor
        from app.vk_api.accessor import VkApiAccessor

        self.app = app
        self.vk_api = VkApiAccessor(app)
        self.bots_manager = BotManager(app)
        self.chats = ChatAccesor(app)
        self.players = PlayerAccesor(app)
        self.games = GameAccesor(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
