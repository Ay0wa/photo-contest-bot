import typing
from logging import getLogger

from app.chats.models import ChatStatus
from app.vk_api.dataclasses import Update

from .states.game_processing import BotGameProcessingState
from .states.idle import BotIdleState
from .states.init import BotInitState
from .states.round_processing import BotRoundProcessingState
from .states.start_new_game import BotStartNewGameState

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")
        self.chat = None

    async def handle_updates(self, updates: list[Update]) -> None:
        # ЭТО ТЕСТ, ЧТОБЫ КАЖДЫЙ РАЗ НЕ ДОБАВЛЯТЬ БОТА В ЧАТ
        object_message, message_text = None, None

        object_message = updates[0].object.message
        if object_message:
            message_text = updates[0].object.message.text

        if object_message and message_text == "chat_invite_user":
            self.chat = await self.app.store.chats.create_chat(
                chat_id=updates[0].object.message.peer_id,
                bot_state=ChatStatus.init,
            )
        if object_message and message_text == "chat_invite_user":
            self.init = BotInitState(self.app, self.chat, self.logger)
            await self.init.handle_init_updates(updates=updates)

            self.chat = await self.app.store.chats.update_bot_state(
                self.chat.chat_id,
                bot_state=ChatStatus.idle,
            )

        if self.chat.bot_state == ChatStatus.idle:
            self.idle = BotIdleState(self.app, self.chat, self.logger)

            bot_state = await self.idle.handle_idle_updates(updates=updates)

            if bot_state:
                self.chat = await self.app.store.chats.update_bot_state(
                    chat_id=self.chat.chat_id,
                    bot_state=bot_state,
                )

        if self.chat.bot_state == ChatStatus.start_new_game:
            self.start_new_game = BotStartNewGameState(
                self.app,
                self.chat,
                self.logger,
            )

            self.game = await self.start_new_game.handle_game_updates(
                updates=updates,
            )

            if self.game:
                self.chat = await self.app.store.chats.update_bot_state(
                    chat_id=self.chat.chat_id,
                    bot_state=ChatStatus.round_processing,
                )

        if self.chat.bot_state == ChatStatus.round_processing:
            self.round_processing = BotRoundProcessingState(
                self.app,
                self.chat,
                self.game,
                self.logger,
            )

            await self.round_processing.handle_round_updates()

            self.chat = await self.app.store.chats.update_bot_state(
                chat_id=self.chat.chat_id,
                bot_state=ChatStatus.game_processing,
            )

        if self.chat.bot_state == ChatStatus.game_processing:
            self.game_processing = BotGameProcessingState(
                self.app, self.chat, self.game, self.logger
            )

            await self.game_processing.handle_game_processing_updates()
