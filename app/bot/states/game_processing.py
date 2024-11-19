import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.chats.models import ChatModel
from app.games.models import GameModel


class BotGameProcessingState:
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

    async def handle_game_processing_updates(self):
        self.players = await self.get_players_of_round(
            game_id=self.game.id,
            current_round=self.game.current_round,
        )

        for i in range(len(self.players) - 1):
            player1, player2 = self.players[i], self.players[i + 1]
            await self.send_avatars(player1, player2)

    async def get_players_of_round(self, game_id: int, current_round: int):
        return await self.app.store.players.get_players_by_round(
            game_id=game_id,
            current_round=current_round,
        )

    async def send_avatars(self, player1, player2) -> None:
        upload_photo_player1 = await self.app.store.vk_api.upload_photo(
            image_url=player1.avatar_url,
        )
        upload_photo_player2 = await self.app.store.vk_api.upload_photo(
            image_url=player2.avatar_url,
        )

        player1_photo = await self.app.store.vk_api.save_photo(
            upload_photo_player1,
        )
        player2_photo = await self.app.store.vk_api.save_photo(
            upload_photo_player2,
        )

        await self.app.store.vk_api.send_photos(
            [player1_photo, player2_photo],
            peer_id=self.chat.chat_id,
        )

    async def send_poll(self): ...
