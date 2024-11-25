import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    from app.players.views import PlayerListView

    app.router.add_view("/players.list_players", PlayerListView)
