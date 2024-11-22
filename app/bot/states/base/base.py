import typing
from abc import ABC, abstractmethod

from app.chats.models import ChatState
from app.vk_api.dataclasses import Event, Message

if typing.TYPE_CHECKING:
    from .context import StateContext


class BaseState(ABC):
    state_name: ChatState | None = None

    def __init__(self, context: "StateContext") -> None:
        self.context = context

    async def on_state_enter(self, from_state: ChatState, **kwargs) -> None:
        pass

    async def on_state_exit(self, to_state: ChatState, **kwargs) -> None:
        pass

    async def handle_message(self, message_obj: Message) -> None:
        pass

    async def handle_events(self, event_obj: Event) -> None:
        pass
