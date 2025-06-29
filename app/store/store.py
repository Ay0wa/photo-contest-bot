import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.database.database import Database


class Store:
    def __init__(self, app: "Application", *args, **kwargs):
        from app.admin.accessor import AdminAccessor
        from app.bot.manager import BotManager
        from app.chats.accessor import ChatAccessor
        from app.games.accessor import GameAccessor
        from app.players.accessor import PlayerAccessor
        from app.vk_api.accessor import VkApiAccessor

        self.app = app
        self.admins = AdminAccessor(app)
        self.vk_api = VkApiAccessor(app)
        self.bots_manager = BotManager(app)
        self.chats = ChatAccessor(app)
        self.players = PlayerAccessor(app)
        self.games = GameAccessor(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
