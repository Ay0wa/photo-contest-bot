from app.bot.bot_messages import INIT_MESSAGE
from app.chats.models import ChatState
from app.vk_api.dataclasses import Event, Message

from .base.base import BaseState


class BotInitState(BaseState):
    state_name = ChatState.init

    async def handle_message(self, message_obj: Message) -> None:
        await self.start()

    async def handle_events(self, event_obj: Event) -> None:
        await self.start()

    async def start(self) -> None:
        self.chat = await self.app.store.chats.get_or_create_chat(
            chat_id=self.chat_id,
        )
        await self.app.store.games.cancel_in_progress_game(chat_id=self.chat_id)
        await self.app.store.vk_api.send_message(
            message=Message(
                text=INIT_MESSAGE,
            ),
            peer_id=self.chat.chat_id,
        )
        await self.context.change_current_state(
            new_state=ChatState.idle,
        )
