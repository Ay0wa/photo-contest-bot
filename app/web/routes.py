from aiohttp.web_app import Application

__all__ = ("setup_routes",)


def setup_routes(app: Application):
    from app.admin.routes import setup_routes as admin_setup_routes
    from app.chats.routes import setup_routes as chats_setup_routes
    from app.games.routes import setup_routes as games_setup_routes
    from app.players.routes import setup_routes as players_setup_routes

    admin_setup_routes(app)
    chats_setup_routes(app)
    games_setup_routes(app)
    players_setup_routes(app)
