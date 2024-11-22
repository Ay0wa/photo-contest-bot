import typing

from app.bot.states.base.base import BaseState
from app.chats.models import ChatState
from app.games.models import GameModel
from app.vk_api.dataclasses import Event, Message

if typing.TYPE_CHECKING:
    from app.bot.states.base.context import StateContext
    from app.web.app import Application


class BotRoundProcessingState(BaseState):

    state_name = ChatState.round_processing

    def __init__(self, context: "StateContext"):
        self.context: "StateContext" | None = None
        super().__init__(context=context)
        self.app: "Application" = self.context.app
        self.chat_id = self.context.chat_id

    async def on_state_enter(
        self, from_state: ChatState, game: GameModel, **kwargs
    ) -> None:
        await self.app.store.players.reset_votes_for_players_in_game(
            game_id=game.id,
        )
        game = await self.app.store.games.update_current_round(
            game_id=game.id,
        )
        await self.send_message(game=game)
        await self.context.change_current_state(
            new_state=ChatState.game_processing,
            game=game,
        )

    async def handle_events(self, event_obj: Event) -> None:
        if event_obj.payload.button == "cancel_game":
            await self.context.change_current_state(
                new_state=ChatState.idle,
            )

    async def get_players(self, game_id: int):
        return await self.app.store.players.get_players_by_id(
            game_id=game_id,
        )

    async def send_message(self, game: GameModel) -> None:
        await self.app.store.vk_api.send_message(
            message=Message(
                text=f"{game.current_round} РАУНД НАЧИНАЕТСЯ!!!",
            ),
            peer_id=self.chat_id,
        )

    async def get_game(self):
        return await self.app.store.games.get_game_by_chat_id(
            chat_id=self.chat_id,
        )
