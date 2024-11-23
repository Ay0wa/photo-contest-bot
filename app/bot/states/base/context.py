import typing

from app.chats.models import ChatState
from app.games.models import GameModel
from app.web.app import Application

if typing.TYPE_CHECKING:
    from .base import BaseState


class StateContext:
    def __init__(self, app: Application, chat_id: int) -> None:
        self.app: "Application" = app
        self.chat_id = chat_id
        self.state: None | "BaseState" = None

    async def get_state(self) -> "BaseState":
        self.state = await self._get_current_state(self.chat_id)
        return self.state

    async def _get_current_state(self, chat_id: int) -> "BaseState":
        from .states import states  # noqa: PLC0415

        chat = await self.app.store.chats.get_or_create_chat(
            chat_id=chat_id,
        )
        return states[chat.bot_state](
            context=self,
        )

    async def change_current_state(
        self,
        new_state: ChatState,
        payload: dict | None = None,
    ) -> None:
        await self.state.on_state_exit(
            to_state=new_state,
        )
        await self.app.store.chats.update_bot_state(
            chat_id=self.chat_id,
            new_state=new_state,
        )
        self.state = await self._get_current_state(
            chat_id=self.chat_id,
        )
        await self.state.on_state_enter(
            from_state=new_state,
        )