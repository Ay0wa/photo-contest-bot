from app.bot.bot_messages import (
    NEW_GAME_PERMISSION_MESSAGE,
    NEW_GAME_WARNING_MESSAGE,
)
from app.bot.states.base.base import BaseState
from app.chats.models import ChatState
from app.games.models import GameModel
from app.players.models import PlayerModel
from app.vk_api.dataclasses import Message, ProfileList


class BotStartNewGameState(BaseState):
    state_name = ChatState.start_new_game

    async def on_state_enter(self, from_state: ChatState, **kwargs) -> None:
        self.game = await self.create_game()
        profiles = await self.get_profiles()

        if len(profiles) > 2:
            await self.create_players(
                profiles=profiles,
                game_id=self.game.id,
            )
            await self.context.change_current_state(
                new_state=ChatState.round_processing,
                game=self.game,
            )
        else:
            await self.send_count_players_warning()
            await self.context.change_current_state(
                new_state=ChatState.idle,
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
        try:
            members = await self.app.store.vk_api.get_chat_members(
                peer_id=self.chat_id,
            )
        except UnboundLocalError:
            await self.send_permission_warning()
            await self.context.change_current_state(
                new_state=ChatState.idle,
                game=self.game,
            )
            return []
        return members.profiles

    async def send_count_players_warning(self):
        await self.app.store.vk_api.send_message(
            message=Message(
                text=NEW_GAME_WARNING_MESSAGE,
            ),
            peer_id=self.chat_id,
        )

    async def send_permission_warning(self):
        await self.app.store.vk_api.send_message(
            message=Message(
                text=NEW_GAME_PERMISSION_MESSAGE,
            ),
            peer_id=self.chat_id,
        )
