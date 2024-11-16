import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


class ChatAccesor():
    def __init__(self, app: "Application"):
        self.app = app
