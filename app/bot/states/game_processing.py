from app.bot.bot_messages import (
    GAME_PROCESSING_START_VOTING,
    GAME_PROCESSING_TIE_MESSAGE,
    GAME_PROCESSING_VOTE_WARNING_MESSAGE,
    GAME_PROCESSING_WINNER_MESSAGE,
)
from app.bot.states.base.base import BaseState
from app.chats.models import ChatState
from app.games.models import GameModel, GameStatus
from app.players.models import PlayerModel, PlayerStatus
from app.vk_api.dataclasses import Event, Message
from app.bot.enums import PayloadButton


class BotGameProcessingState(BaseState):
    state_name = ChatState.game_processing

    async def on_state_enter(
        self, from_state: ChatState, **kwargs
    ) -> None:
        game = await self.app.store.games.get_game_by_status(
            chat_id=self.chat_id,
            status=GameStatus.in_progress,
        )
        players = await self.app.store.players.get_players_by_round(
            game_id=game.id,
            current_round=game.current_round,
            status=PlayerStatus.voting,
        )
        if len(players) == 1:
            await self.app.store.players.update_player_status(
                game_id=game.id,
                player_id=players[0].id,
                status=PlayerStatus.winner,
            )
            await self.context.change_current_state(
                new_state=ChatState.game_finished,
                game=game,
            )

        players = await self.app.store.players.set_players_in_game(
            game_id=game.id,
            player_ids=[players[0].user_id, players[1].user_id],
        )

        player1 = players[0]
        player2 = players[1]

        await self._send_avatars(
            player1,
            player2,
        )
        await self._send_keyboard(
            players=[player1.username, player2.username],
        )

    async def handle_events(self, event_obj: Event) -> None:
        game = await self.app.store.games.get_game_by_status(
            chat_id=self.chat_id,
            status=GameStatus.in_progress,
        )
        if event_obj.payload.button == PayloadButton.cancel_game:
            await self.context.change_current_state(
                new_state=ChatState.idle,
            )
            await self.app.store.games.cancel_in_progress_game(chat_id=self.chat_id)
            await self.app.store.vk_api.send_event_answer(
                event_obj=event_obj,
            )
            return
        player = event_obj.payload.button
        user_voted_id = event_obj.from_id

        user = await self.app.store.players.get_player_by_user_id(
            game_id=game.id,
            user_id=user_voted_id,
        )
        if not user.is_voted and (
            user.status == PlayerStatus.voting
            or user.status == PlayerStatus.loser
        ):
            await self.app.store.players.update_voted(
                game_id=game.id,
                player_id=user.id,
                new_voted=True,
            )
            await self.app.store.players.update_votes_by_username(
                username=player,
                game_id=game.id,
            )
        else:
            await self._send_vote_warning(
                username_voted=user.username,
            )

        if await self.app.store.players.check_all_votes_true_for_game(
            game_id=game.id,
        ):
            await self.context.change_current_state(
                new_state=ChatState.round_processing,
            )
            await self.app.store.vk_api.send_event_answer(
                event_obj=event_obj,
            )
            return
        await self.app.store.vk_api.send_event_answer(
            event_obj=event_obj,
        )

    async def on_state_exit(self, to_state: ChatState, **kwargs) -> None:
        if to_state != ChatState.game_finished:
            game = await self.app.store.games.get_game_by_status(
                chat_id=self.chat_id,
                status=GameStatus.in_progress,
            )
            player_winner = (
                await self.app.store.players.get_player_with_max_votes(
                    game_id=game.id,
                )
            )
            player_loser = (
                await self.app.store.players.get_player_with_min_votes(
                    game_id=game.id,
                )
            )
            await self._send_result(
                game=game,
                winner=player_winner,
                loser=player_loser,
            )

    async def _send_avatars(self, player1, player2) -> None:
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
            peer_id=self.chat_id,
        )

    async def _send_result(
        self,
        game,
        winner: PlayerModel,
        loser: PlayerModel,
    ):
        if winner.votes != loser.votes:
            await self.app.store.players.update_player_status(
                game_id=game.id,
                player_id=winner.id,
                status=PlayerStatus.voting,
            )
            await self.app.store.players.update_player_status(
                game_id=game.id,
                player_id=loser.id,
                status=PlayerStatus.loser,
            )
            await self.app.store.vk_api.send_message(
                message=Message(
                    text=GAME_PROCESSING_WINNER_MESSAGE.format(
                        winner=winner.username,
                        winner_votes=winner.votes,
                        loser=loser.username,
                        loser_votes=loser.votes,
                    )
                ),
                peer_id=self.chat_id,
            )
        else:
            await self.app.store.vk_api.send_message(
                message=Message(
                    text=GAME_PROCESSING_TIE_MESSAGE.format(
                        username1=winner.username,
                        votes1=winner.votes,
                        username2=loser.username,
                        votes2=loser.votes,
                    )
                ),
                peer_id=self.chat_id,
            )

    async def _send_vote_warning(self, username_voted: str):
        await self.app.store.vk_api.send_message(
            message=Message(
                text=GAME_PROCESSING_VOTE_WARNING_MESSAGE.format(
                    username=username_voted,
                ),
            ),
            peer_id=self.chat_id,
        )

    async def _send_keyboard(
        self,
        players: list[str],
    ):
        keyboard = {
            "one_time": False,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "callback",
                            "payload": f'{{"button": "{players[0]}"}}',
                            "label": players[0],
                        },
                        "color": "primary",
                    },
                    {
                        "action": {
                            "type": "callback",
                            "payload": f'{{"button": "{players[1]}"}}',
                            "label": players[1],
                        },
                        "color": "primary",
                    },
                ],
                [
                    {
                        "action": {
                            "type": "callback",
                            "payload": f'{{"button": "cancel_game"}}',
                            "label": "Закончить игру",
                        },
                        "color": "negative",
                    },
                ],
            ],
        }

        await self.app.store.vk_api.send_message(
            message=Message(
                GAME_PROCESSING_START_VOTING.format(
                    username1=players[0],
                    username2=players[1],
                ),
            ),
            peer_id=self.chat_id,
            keyboard=keyboard,
        )
