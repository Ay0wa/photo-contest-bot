import random
import typing

from app.chats.models import ChatModel
from app.games.models import GameModel
from app.vk_api.dataclasses import Message

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotRoundProcessingState:
    def __init__(
        self,
        app: "Application",
        chat: ChatModel,
        game: GameModel,
        logger,
    ):
        self.app = app
        self.bot = None
        self.logger = logger
        self.chat = chat
        self.game = game

    async def handle_round_updates(self) -> None:
        players = await self.app.store.players.get_players_by_round(
            game_id=self.game.id,
            current_round=self.game.current_round,
        )

        if len(players) % 2 != 0:
            await self.app.store.players.update_round(
                player_id=players[random.randint(0, len(players))].id,
                new_round=self.game.current_round + 1,
            )
        await self.send_message()

    async def get_players(self, game_id: int):
        return await self.app.store.players.get_players_by_id(
            game_id=game_id,
        )

    async def send_message(self) -> None:
        await self.app.store.vk_api.send_message(
            message=Message(
                text=f"{self.game.current_round} РАУНД НАЧИНАЕТСЯ!!!",
            ),
            peer_id=self.chat.chat_id,
        )
