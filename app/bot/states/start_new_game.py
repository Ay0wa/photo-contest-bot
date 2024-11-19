import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.chats.models import ChatModel
from app.games.models import GameModel
from app.players.models import PlayerModel
from app.vk_api.dataclasses import (
    ProfileList,
    Update,
)


class BotStartNewGameState:
    def __init__(self, app: "Application", chat: ChatModel, logger):
        self.app = app
        self.bot = None
        self.logger = logger
        self.chat = chat

    async def handle_game_updates(
        self,
        updates: list[Update],
    ) -> GameModel | None:
        for update in updates:
            if update.object.payload.button == "start_game":
                game = await self.create_game()
                profiles = await self.get_profiles()
                await self.create_players(
                    profiles=profiles,
                    game_id=game.id,
                )
                return game
        return None

    async def create_game(self) -> GameModel:
        return await self.app.store.games.create_game(
            chat_id=self.chat.chat_id,
        )

    async def create_players(
        self, profiles: ProfileList, game_id: int
    ) -> list[PlayerModel]:
        players = []
        for profile in profiles:
            player = await self.app.store.players.create_player(
                username=profile.screen_name,
                avatar_url=profile.photo_100,
                game_id=game_id,
            )
            players.append(player)
        return players

    async def get_profiles(self):
        members = await self.app.store.vk_api.get_chat_members(
            peer_id=self.chat.chat_id,
        )
        return members.profiles

    async def get_last_game(self):
        return await self.app.store.games.get_last_game(
            chat_id=self.chat.chat_id,
        )
