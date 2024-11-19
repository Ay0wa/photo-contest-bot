import typing

from app.bot.bot_messages import IDLE_MESSAGE
from app.chats.models import ChatModel, ChatStatus
from app.vk_api.dataclasses import (
    Message,
    Update,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotIdleState:
    def __init__(self, app: "Application", chat: ChatModel, logger):
        self.app = app
        self.bot = None
        self.logger = logger
        self.chat = chat

    async def handle_idle_updates(self, updates: list[Update]) -> None:
        state = self.chat.bot_state
        for update in updates:
            if update.type == "message_event":
                state = await self.handle_idle_action(update=update)
            elif update.object.message.text == "keyboard":
                await self.app.store.vk_api.send_keyboard(
                    peer_id=self.chat.chat_id,
                )
        return state

    async def handle_idle_action(self, update: Update) -> ChatStatus | None:
        if update.object.payload.button == "start_game":
            await self.start_game_button(update=update)
            return ChatStatus.start_new_game
        if update.object.payload.button == "get_last_game":
            await self.send_last_game(update=update)
            return ChatStatus.idle
        return None

    async def start_game_button(self, update: Update) -> None:
        await self.app.store.vk_api.send_message(
            message=Message(
                user_id=update.object.user_id,
                text=IDLE_MESSAGE,
            ),
            peer_id=self.chat.chat_id,
        )

    async def send_last_game(self, update: Update):
        last_game = await self.app.store.games.get_last_game(
            chat_id=self.chat.chat_id,
        )
        await self.app.store.vk_api.send_message(
            message=Message(
                text=f"Результат последней игры: {last_game.created_at}",
            ),
            peer_id=self.chat.chat_id,
        )
