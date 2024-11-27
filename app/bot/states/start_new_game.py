from app.bot.bot_messages import (
    NEW_GAME_PERMISSION_MESSAGE,
    NEW_GAME_WARNING_MESSAGE,
)
from app.bot.states.base.base import BaseState
from app.chats.models import ChatState
from app.players.models import PlayerModel
from app.vk_api.dataclasses import Message, ProfileList


class BotStartNewGameState(BaseState):
    state_name = ChatState.start_new_game

    async def on_state_enter(self, from_state: ChatState, **kwargs) -> None:
        try:
            profiles = await self._get_profiles()
        except Exception:
            await self._send_permission_warning()
            await self.context.change_current_state(
                new_state=ChatState.idle,
            )
            return

        if len(profiles) > 2:
            game = await self.app.store.games.create_game(
                chat_id=self.chat_id,
            )
            await self._create_players(
                profiles=profiles,
                game_id=game.id,
            )
            await self.context.change_current_state(
                new_state=ChatState.round_processing,
            )
        else:
            await self._send_count_players_warning()
            await self.context.change_current_state(
                new_state=ChatState.idle,
            )

    async def _create_players(
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

    async def _get_profiles(self):
        members = await self.app.store.vk_api.get_chat_members(
            peer_id=self.chat_id,
        )
        return members.profiles

    async def _send_count_players_warning(self):
        await self.app.store.vk_api.send_message(
            message=Message(
                text=NEW_GAME_WARNING_MESSAGE,
            ),
            peer_id=self.chat_id,
        )

    async def _send_permission_warning(self):
        await self.app.store.vk_api.send_message(
            message=Message(
                text=NEW_GAME_PERMISSION_MESSAGE,
            ),
            peer_id=self.chat_id,
        )
