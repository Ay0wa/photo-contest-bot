import typing

from app.bot.bot_messages import IDLE_MESSAGE, KEYBOARD
from app.bot.states.base.base import BaseState
from app.chats.models import ChatState
from app.vk_api.dataclasses import Event, Message

if typing.TYPE_CHECKING:
    from app.bot.states.base.context import StateContext
    from app.web.app import Application


class BotIdleState(BaseState):

    state_name = ChatState.idle

    def __init__(self, context: "StateContext"):
        self.context: "StateContext" | None = None
        super().__init__(context=context)
        self.app: "Application" = self.context.app
        self.chat_id = self.context.chat_id

    async def on_state_enter(self, from_state: ChatState, **kwargs) -> None:
        await self.app.store.vk_api.send_message(
            message=Message(text="На клаву"),
            peer_id=self.chat_id,
            keyboard=KEYBOARD,
        )

    async def handle_events(self, event_obj: Event) -> None:
        if event_obj.payload.button == "start_game":
            await self.start_game_button()
            await self.context.change_current_state(
                new_state=ChatState.start_new_game,
            )
        elif event_obj.payload.button == "get_last_game":
            await self.send_last_game()

    async def handle_message(self, message_obj: Message) -> None:
        if message_obj.text == "keyboard":
            await self.app.store.vk_api.send_message(
                message=Message(text="На клаву"),
                peer_id=self.chat_id,
                keyboard=KEYBOARD,
            )

    async def on_state_exit(self, to_state: ChatState, **kwargs) -> None: ...

    async def start_game_button(self) -> None:
        await self.app.store.vk_api.send_message(
            message=Message(
                text=IDLE_MESSAGE,
            ),
            peer_id=self.chat_id,
        )

    async def send_last_game(self):
        last_game = await self.app.store.games.get_last_game(
            chat_id=self.chat_id,
        )
        if last_game:
            text = f"Результат последней игры: {last_game.created_at}"
        else:
            text = "Еще ни одной игры не было сыграно"
        await self.app.store.vk_api.send_message(
            message=Message(
                text=text,
            ),
            peer_id=self.chat_id,
        )
