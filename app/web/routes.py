from aiohttp.web_app import Application

__all__ = ("setup_routes",)


def setup_routes(app: Application):
    from app.admin.routes import setup_routes as admin_setup_routes
    from app.chats.routes import setup_routes as chat_setup_routes

    admin_setup_routes(app)
    chat_setup_routes(app)
