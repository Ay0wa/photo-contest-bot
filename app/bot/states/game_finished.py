from app.bot.bot_messages import GAME_FINISHED_END_MESSAGE
from app.bot.states.base.base import BaseState
from app.chats.models import ChatState
from app.games.models import GameStatus
from app.players.models import PlayerStatus
from app.vk_api.dataclasses import Message


class BotGameFinishedState(BaseState):
    state_name = ChatState.game_finished

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

    async def send_winner(self, username_winner) -> None:
        await self.app.store.vk_api.send_message(
            message=Message(
                text=GAME_FINISHED_END_MESSAGE.format(username=username_winner),
            ),
            peer_id=self.chat_id,
        )
