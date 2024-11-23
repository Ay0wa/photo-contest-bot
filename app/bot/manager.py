import typing
from logging import getLogger

from app.chats.models import ChatModel
from app.vk_api.dataclasses import Event, Message, Payload, Update

from .states.base.base import BaseState
from .states.base.context import StateContext

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")
        self.chat: None | ChatModel = None
        self.state_context: None | StateContext = None
        self.current_state: None | BaseState = None

    async def handle_updates(self, updates: list[Update]) -> None:
        event_obj, message_obj = None, None
        for update in updates:
            if update.object.message:
                chat_id = update.object.message.peer_id
                message_obj = Message(
                    text=update.object.message.text,
                )
            else:
                chat_id = update.object.peer_id
                event_obj = Event(
                    event_id=update.object.event_id,
                    from_id=update.object.user_id,
                    peer_id=update.object.peer_id,
                    payload=Payload(
                        button=update.object.payload.button,
                    ),
                )

        self.state_context = StateContext(
            app=self.app,
            chat_id=chat_id,
        )
        self.current_state = await self.state_context.init_state()
        if event_obj:
            await self.current_state.handle_events(
                event_obj=event_obj,
            )
        elif message_obj:
            await self.current_state.handle_message(
                message_obj=message_obj,
            )
