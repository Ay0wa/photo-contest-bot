import typing

from app.bot.states.base.base import BaseState
from app.bot.states.base.context import StateContext
from app.chats.models import ChatState
from app.games.models import GameModel
from app.players.models import PlayerModel
from app.vk_api.dataclasses import ProfileList

if typing.TYPE_CHECKING:
    from app.bot.states.base.context import StateContext
    from app.web.app import Application


class BotStartNewGameState(BaseState):

    state_name = ChatState.start_new_game

    def __init__(self, context: "StateContext"):
        self.context: "StateContext" | None = None
        super().__init__(context=context)
        self.app: "Application" = self.context.app
        self.chat_id = self.context.chat_id

    async def on_state_enter(self, from_state: ChatState, **kwargs) -> None:
        self.game = await self.create_game()
        profiles = await self.get_profiles()
        await self.create_players(
            profiles=profiles,
            game_id=self.game.id,
        )
        await self.context.change_current_state(
            new_state=ChatState.round_processing,
            game=self.game,
        )

    async def create_game(self) -> GameModel:
        return await self.app.store.games.create_game(
            chat_id=self.chat_id,
        )

    async def create_players(
        self, profiles: ProfileList, game_id: int
    ) -> list[PlayerModel]:
        players = []
        for profile in profiles:
            player = await self.app.store.players.create_player(
                user_id=profile.id,
                username=profile.screen_name,
                avatar_url=profile.photo_100,
                game_id=game_id,
            )
            players.append(player)
        return players

    async def get_profiles(self):
        members = await self.app.store.vk_api.get_chat_members(
            peer_id=self.chat_id,
        )
        return members.profiles

    async def get_last_game(self):
        return await self.app.store.games.get_last_game(
            chat_id=self.chat_id,
        )
