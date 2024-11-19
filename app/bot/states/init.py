import typing

from app.bot.bot_messages import KEYBOARD_MESSAGE
from app.chats.models import ChatModel
from app.vk_api.dataclasses import (
    Message,
    Update,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotInitState:
    def __init__(self, app: "Application", chat: ChatModel, logger):
        self.app = app
        self.chat = chat
        self.logger = logger

    async def handle_init_updates(self, updates: list[Update]) -> None:
        await self.start()

    async def start(self):
        await self.app.store.vk_api.send_message(
            message=Message(
                text=KEYBOARD_MESSAGE,
            ),
            peer_id=self.chat.chat_id,
        )
