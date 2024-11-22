import typing

from app.bot.states.base.base import BaseState
from app.chats.models import ChatState
from app.games.models import GameModel, GameStatus
from app.players.models import PlayerModel, PlayerStatus
from app.vk_api.dataclasses import Event, Message

if typing.TYPE_CHECKING:
    from app.bot.states.base.context import StateContext
    from app.web.app import Application


class BotGameProcessingState(BaseState):

    state_name = ChatState.game_processing

    def __init__(self, context: "StateContext"):
        self.context: "StateContext" | None = None
        super().__init__(context=context)
        self.app: "Application" = self.context.app
        self.chat_id = self.context.chat_id

    async def on_state_enter(
        self, from_state: ChatState, game: GameModel, **kwargs
    ) -> None:
        self.game = game
        self.players = await self.app.store.players.get_players_by_round(
            game_id=game.id,
            current_round=game.current_round,
            status=PlayerStatus.voting,
        )
        if len(self.players) == 1:
            await self.app.store.players.update_player_status(
                game_id=game.id,
                player_id=self.players[0].id,
                status=PlayerStatus.winner,
            )
            await self.context.change_current_state(
                new_state=ChatState.game_finished,
                game=game,
            )

        self.players = await self.app.store.players.update_players_status(
            game_id=game.id,
            player_ids=[self.players[0].user_id, self.players[1].user_id],
        )

        player1 = self.players[0]
        player2 = self.players[1]

        await self.send_avatars(
            player1,
            player2,
        )
        await self.send_poll(
            players=[player1.username, player2.username],
        )

    async def handle_events(self, event_obj: Event) -> None:
        game = await self.app.store.games.get_game_by_status(
            chat_id=self.chat_id,
            status=GameStatus.in_progress,
        )
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
            await self.send_message(
                username_voted=user.username,
            )

        if await self.app.store.players.check_all_votes_true_for_game(
            game_id=game.id,
        ):
            await self.context.change_current_state(
                new_state=ChatState.round_processing,
                game=game,
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
            await self.app.store.players.update_player_status(
                game_id=game.id,
                player_id=player_winner.id,
                status=PlayerStatus.voting,
            )
            await self.app.store.players.update_player_status(
                game_id=game.id,
                player_id=player_loser.id,
                status=PlayerStatus.loser,
            )

            await self.send_result(
                player_username=player_winner.username,
            )

    async def get_players_by_round(
        self,
        game_id: int,
        current_round: int,
    ) -> list[PlayerModel]:
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
            peer_id=self.chat_id,
        )

    async def send_result(self, player_username: str):
        await self.app.store.vk_api.send_message(
            message=Message(
                text=f"{player_username} ПОБЕДИЛ!",
            ),
            peer_id=self.chat_id,
        )

    async def send_message(self, username_voted: str):
        await self.app.store.vk_api.send_message(
            message=Message(
                text=f"""{username_voted}, Вы участвуете в раунде,
                либо вы уже проголосовали!""",
            ),
            peer_id=self.chat_id,
        )

    async def send_poll(
        self,
        players: list[str],
    ):
        keyboard = {
            "one_time": True,
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
                ]
            ],
        }

        await self.app.store.vk_api.send_message(
            message=Message(
                text="Начинаем голосование!",
            ),
            peer_id=self.chat_id,
            keyboard=keyboard,
        )
