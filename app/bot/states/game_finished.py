import typing

from app.bot.states.base.base import BaseState
from app.chats.models import ChatState
from app.games.models import GameStatus
from app.players.models import PlayerStatus
from app.vk_api.dataclasses import Message
from app.web.app import Application

if typing.TYPE_CHECKING:
    from app.bot.states.base.context import StateContext


class BotGameFinishedState(BaseState):

    state_name = ChatState.game_finished

    def __init__(self, context: "StateContext"):
        self.context: "StateContext" | None = None
        super().__init__(context=context)
        self.app: "Application" = self.context.app
        self.chat_id = self.context.chat_id

    async def on_state_enter(self, from_state: ChatState, **kwargs) -> None:
        game = await self.app.store.games.get_game_by_status(
            chat_id=self.chat_id,
            status=GameStatus.in_progress,
        )
        player = await self.app.store.players.get_player_by_status(
            game_id=game.id,
            status=PlayerStatus.winner,
        )
        await self.send_winner(
            username_winner=player.username,
        )
        await self.app.store.games.update_game_status(
            game_id=game.id,
            new_status=GameStatus.canceled,
        )
        await self.context.change_current_state(
            new_state=ChatState.init,
        )

    async def on_state_exit(self, to_state: ChatState, **kwargs) -> None: ...

    async def send_winner(self, username_winner) -> None:
        await self.app.store.vk_api.send_message(
            message=Message(
                text=f"Победитель: {username_winner}",
            ),
            peer_id=self.chat_id,
        )
