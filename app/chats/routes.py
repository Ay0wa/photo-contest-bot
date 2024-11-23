import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    from app.chats.views import ChatListView

    app.router.add_view("/chats.list_chats", ChatListView)
