import typing

from app.bot.bot_messages import KEYBOARD_MESSAGE
from app.chats.models import ChatState
from app.vk_api.dataclasses import Message

from .base.base import BaseState

if typing.TYPE_CHECKING:
    from app.bot.states.base.context import StateContext
    from app.web.app import Application


class BotInitState(BaseState):

    state_name = ChatState.init

    def __init__(self, context: "StateContext"):
        self.context: "StateContext" | None = None
        super().__init__(context=context)
        self.app: Application = self.context.app
        self.chat_id = self.context.chat_id

    async def on_state_enter(self, from_state: ChatState, **kwargs) -> None:
        self.chat = await self.app.store.chats.create_chat(
            chat_id=self.chat_id,
        )
        await self.cancel_in_progress_games()
        await self.start()
        await self.context.change_current_state(
            new_state=ChatState.idle,
        )

    async def on_state_exit(self, to_state: ChatState, **kwargs) -> None: ...

    async def start(self) -> None:
        await self.app.store.vk_api.send_message(
            message=Message(
                text=KEYBOARD_MESSAGE,
            ),
            peer_id=self.chat.chat_id,
        )

    async def cancel_in_progress_games(self) -> None:
        await self.app.store.games.cancel_in_progress_game(
            chat_id=self.chat_id,
        )
