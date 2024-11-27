from app.bot.bot_messages import ROUND_START_MESSAGE
from app.bot.states.base.base import BaseState
from app.chats.models import ChatState
from app.games.models import GameModel, GameStatus
from app.players.models import PlayerStatus
from app.vk_api.dataclasses import Message


class BotRoundProcessingState(BaseState):
    state_name = ChatState.round_processing

    async def on_state_enter(self, from_state: ChatState, **kwargs) -> None:
        game = await self.app.store.games.get_game_by_status(
            chat_id=self.chat_id,
            status=GameStatus.in_progress,
        )
        players = await self.app.store.players.get_players_by_status(
            game_id=game.id,
            status=PlayerStatus.voting,
        )
        await self.app.store.players.reset_votes_for_players_in_game(
            game_id=game.id,
        )
        if len(players) != 1:
            game = await self.app.store.games.update_current_round(
                game_id=game.id,
            )
            await self._send_message(game=game)
        await self.context.change_current_state(
            new_state=ChatState.game_processing,
        )

    async def _send_message(self, game: GameModel) -> None:
        await self.app.store.vk_api.send_message(
            message=Message(
                text=ROUND_START_MESSAGE.format(
                    current_round=game.current_round
                ),
            ),
            peer_id=self.chat_id,
        )
