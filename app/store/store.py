import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application", *args, **kwargs):
        # from app.users.accessor import UserAccessor
        from app.bot.manager import BotManager
        from app.vk_api.accessor import VkApiAccessor

        self.app = app
        # self.user = UserAccessor(self)
        self.vk_api = VkApiAccessor(app)
        self.bots_manager = BotManager(app)


def setup_store(app: "Application"):
    app.store = Store(app)
