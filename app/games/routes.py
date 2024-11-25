import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    from app.games.views import GameListView

    app.router.add_view("/games.list_games", GameListView)
