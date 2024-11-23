from app.bot.bot_messages import (
    IDLE_COMMANDS_MESSAGE,
    IDLE_LAST_GAME_MESSAGE,
    IDLE_NONE_GAMES,
    IDLE_RULES_MESSAGE,
    IDLE_START_GAME_MESSAGE,
    IDLE_UNKNOWN_COMMAND,
    IDLE_WITH_KEYBOARD_MESSAGE,
    MAIN_KEYBOARD,
)
from app.bot.enums import PayloadButton
from app.bot.states.base.base import BaseState
from app.chats.models import ChatState
from app.players.models import PlayerStatus
from app.vk_api.dataclasses import Event, Message


class BotIdleState(BaseState):
    state_name = ChatState.idle

    async def on_state_enter(self, from_state: ChatState, **kwargs) -> None:
        await self.app.store.vk_api.send_message(
            message=Message(text=IDLE_COMMANDS_MESSAGE),
            peer_id=self.chat_id,
            keyboard=MAIN_KEYBOARD,
        )

    async def handle_events(self, event_obj: Event) -> None:
        if event_obj.payload.button == PayloadButton.start_game:
            await self._start_game_button()
            await self.context.change_current_state(
                new_state=ChatState.start_new_game,
            )
        elif event_obj.payload.button == PayloadButton.get_last_game:
            await self._get_last_game_button()
        await self.app.store.vk_api.send_event_answer(
            event_obj=event_obj,
        )

    async def handle_message(self, message_obj: Message) -> None:
        if message_obj.text == "/keyboard":
            await self.app.store.vk_api.send_message(
                message=Message(text=IDLE_WITH_KEYBOARD_MESSAGE),
                peer_id=self.chat_id,
                keyboard=MAIN_KEYBOARD,
            )
        elif message_obj.text == "/help":
            await self.app.store.vk_api.send_message(
                message=Message(text=IDLE_COMMANDS_MESSAGE),
                peer_id=self.chat_id,
            )
        elif message_obj.text == "/rules":
            await self.app.store.vk_api.send_message(
                message=Message(text=IDLE_RULES_MESSAGE),
                peer_id=self.chat_id,
                keyboard=MAIN_KEYBOARD,
            )
        elif message_obj.text[0] == "/":
            await self.app.store.vk_api.send_message(
                message=Message(text=IDLE_UNKNOWN_COMMAND),
                peer_id=self.chat_id,
            )

    async def _start_game_button(self) -> None:
        await self.app.store.vk_api.send_message(
            message=Message(
                text=IDLE_START_GAME_MESSAGE,
            ),
            peer_id=self.chat_id,
        )

    async def _get_last_game_button(self):
        last_game = await self.app.store.games.get_last_game(
            chat_id=self.chat_id,
        )
        if last_game:
            winner = await self.app.store.players.get_player_by_status(
                game_id=last_game.id,
                status=PlayerStatus.winner,
            )
            text = IDLE_LAST_GAME_MESSAGE.format(username=winner.username)
        else:
            text = IDLE_NONE_GAMES
        await self.app.store.vk_api.send_message(
            message=Message(
                text=text,
            ),
            peer_id=self.chat_id,
        )
