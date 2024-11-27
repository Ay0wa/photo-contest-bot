from sqlalchemy import or_, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.base.base_accessor import BaseAccessor

from .models import PlayerModel, PlayerStatus


class PlayerAccessor(BaseAccessor):
    async def create_player(
        self, user_id: int, username: str, avatar_url: str, game_id: int
    ) -> PlayerModel:
        async with self.app.database.session() as session:
            player = PlayerModel(
                user_id=user_id,
                username=username,
                avatar_url=avatar_url,
                game_id=game_id,
            )
            try:
                session.add(player)
                await session.commit()
                self.logger.info("Player created successfully")
            except IntegrityError:
                await session.rollback()
                self.logger.error("IntegrityError while creating player")
                raise
            except SQLAlchemyError:
                await session.rollback()
                self.logger.error("SQLAlchemyError while creating player")
                raise
            except Exception:
                await session.rollback()
                self.logger.error("Unexpected error while creating player")
                raise
            return player

    async def get_player_by_id(self, player_id: int) -> PlayerModel | None:
        async with self.app.database.session() as session:
            try:
                query = select(PlayerModel).where(PlayerModel.id == player_id)
                result = await session.execute(query)
                player = result.scalars().first()
                if player:
                    self.logger.info(
                        "Player retrieved by player_id successfully"
                    )
                else:
                    self.logger.warning("Player not found by player_id")
            except SQLAlchemyError:
                self.logger.error(
                    "SQLAlchemyError while retrieving player by game_id"
                )
                raise
            except Exception:
                self.logger.error(
                    "Unexpected error while retrieving player by game_id"
                )
                raise
            return player

    async def get_players_by_game_id(self, game_id: int) -> list[PlayerModel]:
        async with self.app.database.session() as session:
            try:
                query = select(PlayerModel).where(
                    PlayerModel.game_id == game_id
                )
                result = await session.execute(query)
                players = result.scalars().all()
                self.logger.info("Players retrieved by game_id successfully")
            except SQLAlchemyError:
                self.logger.error(
                    "SQLAlchemyError while retrieving players by game_id"
                )
                raise
            except Exception:
                self.logger.error(
                    "Unexpected error while retrieving players by game_id"
                )
                raise
            return players

    async def get_player_by_user_id(
        self, game_id: int, user_id: int
    ) -> PlayerModel | None:
        async with self.app.database.session() as session:
            try:
                query = (
                    select(PlayerModel)
                    .where(PlayerModel.user_id == user_id)
                    .where(PlayerModel.game_id == game_id)
                )
                result = await session.execute(query)
                player = result.scalars().first()
                if player:
                    self.logger.info(
                        "Player retrieved by game_id and user_id successfully"
                    )
                else:
                    self.logger.warning(
                        "Player not found by game_id and user_id"
                    )
            except SQLAlchemyError:
                self.logger.error(
                    "SQLAlchemyError while retrieving player by game_id"
                )
                raise
            except Exception:
                self.logger.error(
                    "Unexpected error while retrieving player by game_id,user_id"  # noqa: E501
                )
                raise
            return player

    async def get_players_by_round(
        self, current_round: int, game_id: int, status: PlayerStatus
    ) -> list[PlayerModel]:
        async with self.app.database.session() as session:
            try:
                query = (
                    select(PlayerModel)
                    .where(PlayerModel.game_id == game_id)
                    .where(PlayerModel.status == status)
                )
                result = await session.execute(query)
                players = result.scalars().all()
                self.logger.info(
                    "Players retrieved for current round successfully"
                )
            except SQLAlchemyError:
                self.logger.error(
                    "SQLAlchemyError while retrieving players for round"
                )
                raise
            except Exception:
                self.logger.error(
                    "Unexpected error while retrieving players for round"
                )
                raise
            return players

    async def get_player_with_max_votes(
        self, game_id: int
    ) -> PlayerModel | None:
        async with self.app.database.session() as session:
            try:
                query = (
                    select(PlayerModel)
                    .where(
                        (PlayerModel.game_id == game_id)
                        & (PlayerModel.status == PlayerStatus.in_game)
                    )
                    .order_by(PlayerModel.votes.desc())
                )
                result = await session.execute(query)
                player = result.scalars().first()
                if player:
                    self.logger.info("Player with maximum votes found")
                else:
                    self.logger.warning("No players with votes found in game")
            except SQLAlchemyError:
                self.logger.error(
                    "SQLAlchemyError while retrieving player with max votes"
                )
                raise
            except Exception:
                self.logger.error(
                    "Unexpected error while retrieving player with max votes"
                )
                raise
            return player

    async def get_player_with_min_votes(
        self, game_id: int
    ) -> PlayerModel | None:
        async with self.app.database.session() as session:
            try:
                query = (
                    select(PlayerModel)
                    .where(
                        (PlayerModel.game_id == game_id)
                        & (PlayerModel.status == PlayerStatus.in_game)
                    )
                    .order_by(PlayerModel.votes.asc())
                )
                result = await session.execute(query)
                player = result.scalars().first()
                if player:
                    self.logger.info("Player with minimum votes found")
                else:
                    self.logger.warning("No players with votes found in game")
            except SQLAlchemyError:
                self.logger.error(
                    "SQLAlchemyError while retrieving player with min votes"
                )
                raise
            except Exception:
                self.logger.error(
                    "Unexpected error while retrieving player with min votes"
                )
                raise
            return player

    async def get_players_by_status(
        self, game_id: int, status: PlayerStatus
    ) -> PlayerModel | None:
        async with self.app.database.session() as session:
            try:
                query = select(PlayerModel).where(
                    (PlayerModel.game_id == game_id)
                    & (PlayerModel.status == status)
                )
                result = await session.execute(query)
                players = result.scalars().all()
                if players:
                    self.logger.info("Player retrieved by status successfully")
                else:
                    self.logger.warning("No player found with given status")
            except SQLAlchemyError:
                self.logger.error(
                    "SQLAlchemyError while retrieving player by status"
                )
                raise
            except Exception:
                self.logger.error(
                    "Unexpected error while retrieving player by status"
                )
                raise
            return players

    async def list_players(self) -> list[PlayerModel]:
        async with self.app.database.session() as session:
            try:
                query = select(PlayerModel)
                result = await session.execute(query)
                games = result.scalars().all()
                self.logger.info("Players retrieved successfully")
            except SQLAlchemyError:
                self.logger.error("SQLAlchemyError during games listing")
                raise
            except Exception:
                self.logger.error("Unexpected error during games listing")
                raise
            return games

    async def get_players_by_filters(self, filters: dict):
        async with self.app.database.session() as session:
            try:
                query = select(PlayerModel)

                if "user_id" in filters:
                    query = query.where(
                        PlayerModel.user_id == filters["user_id"]
                    )

                if "game_id" in filters:
                    query = query.where(
                        PlayerModel.game_id == filters["game_id"]
                    )

                if "status" in filters:
                    query = query.where(PlayerModel.status == filters["status"])

                if "votes" in filters:
                    query = query.where(PlayerModel.votes == filters["votes"])

                if "is_voted" in filters:
                    query = query.where(
                        PlayerModel.is_voted == filters["is_voted"]
                    )

                result = await session.execute(query)
                return result.scalars().all()

            except IntegrityError:
                self.logger.error(
                    "Database error while fetching games with filters"
                )
                await session.rollback()
                raise

            except Exception:
                self.logger.error(
                    "Unknown error while fetching games with filters"
                )
                await session.rollback()
                raise

    async def update_round(self, player_id: int, new_round: int) -> PlayerModel:
        async with self.app.database.session() as session:
            try:
                query = (
                    update(PlayerModel)
                    .values(round=new_round)
                    .where(PlayerModel.id == player_id)
                    .returning(PlayerModel)
                )
                result = await session.execute(query)
                await session.commit()
                self.logger.info(
                    "Round updated successfully for player_id=%s", player_id
                )
                return result.scalar_one()
            except IntegrityError:
                await session.rollback()
                self.logger.error("IntegrityError while updating round")
                raise
            except SQLAlchemyError:
                await session.rollback()
                self.logger.error("SQLAlchemyError while updating round")
                raise
            except Exception:
                await session.rollback()
                self.logger.error("Unexpected error while updating round")
                raise

    async def update_voted(
        self, game_id: int, player_id: int, new_voted: bool
    ) -> PlayerModel:
        async with self.app.database.session() as session:
            try:
                query = (
                    update(PlayerModel)
                    .values(is_voted=new_voted)
                    .where(PlayerModel.id == player_id)
                    .where(PlayerModel.game_id == game_id)
                    .returning(PlayerModel)
                )
                result = await session.execute(query)
                await session.commit()
                self.logger.info(
                    "Vote status updated successfully for player_id",
                )
                return result.scalar_one()
            except SQLAlchemyError:
                await session.rollback()
                self.logger.error(
                    "SQLAlchemyError while updating vote status for player_id",
                )
                raise
            except Exception:
                await session.rollback()
                self.logger.error(
                    "Unexpected error while updating vote status for player_id",
                )
                raise

    async def update_votes_by_username(
        self, username: str, game_id: int
    ) -> PlayerModel:
        async with self.app.database.session() as session:
            try:
                query = (
                    update(PlayerModel)
                    .values(votes=PlayerModel.votes + 1)
                    .where(PlayerModel.username == username)
                    .where(PlayerModel.game_id == game_id)
                    .returning(PlayerModel)
                )
                result = await session.execute(query)
                await session.commit()
                self.logger.info(
                    "Votes updated successfully for username=%s", username
                )
                return result.scalar_one()
            except SQLAlchemyError:
                await session.rollback()
                self.logger.error(
                    "SQLAlchemyError while updating votes for username=%s",
                    username,
                )
                raise
            except Exception:
                await session.rollback()
                self.logger.error(
                    "Unexpected error while updating votes for username=%s",
                    username,
                )
                raise

    async def set_players_in_game(
        self, game_id: int, player_ids: list[int]
    ) -> list[PlayerModel]:
        async with self.app.database.session() as session:
            try:
                query = (
                    update(PlayerModel)
                    .where(
                        (PlayerModel.user_id.in_(player_ids))
                        & (PlayerModel.game_id == game_id)
                    )
                    .values(status=PlayerStatus.in_game)
                    .returning(PlayerModel)
                )
                result = await session.execute(query)
                await session.commit()
                self.logger.info(
                    "Players status updated to in_game for game_id=%s", game_id
                )
                return result.scalars().all()
            except SQLAlchemyError:
                await session.rollback()
                self.logger.error(
                    "SQLAlchemyError while updating players' status to in_game"
                )
                raise
            except Exception:
                await session.rollback()
                self.logger.error(
                    "Unexpected error while updating players' status to in_game"
                )
                raise

    async def update_player_status(
        self, game_id: int, player_id: int, status: PlayerStatus
    ):
        async with self.app.database.session() as session:
            try:
                query = (
                    update(PlayerModel)
                    .where(
                        (PlayerModel.id == player_id)
                        & (PlayerModel.game_id == game_id)
                    )
                    .values(status=status)
                )
                await session.execute(query)
                await session.commit()
                self.logger.info(
                    "Player status updated successfully by player_id,game_id",
                )
            except SQLAlchemyError:
                await session.rollback()
                self.logger.error(
                    "SQLAlchemyError while updating player status by player_id",
                )
                raise
            except Exception:
                await session.rollback()
                self.logger.error(
                    "Unexpected error while updating status by player_id",
                )
                raise

    async def check_all_votes_true_for_game(self, game_id: int) -> bool:
        async with self.app.database.session() as session:
            try:
                query = (
                    select(PlayerModel)
                    .join(PlayerModel.game)
                    .where(PlayerModel.game_id == game_id)
                    .where(
                        or_(
                            PlayerModel.status == PlayerStatus.voting,
                            PlayerModel.status == PlayerStatus.loser,
                        )
                    )
                    .where(PlayerModel.is_voted)
                )
                result = await session.execute(query)
                players = result.scalars().all()

                query_total_players = (
                    select(PlayerModel)
                    .where(PlayerModel.game_id == game_id)
                    .where(
                        or_(
                            PlayerModel.status == PlayerStatus.voting,
                            PlayerModel.status == PlayerStatus.loser,
                        )
                    )
                )
                total_players_result = await session.execute(
                    query_total_players
                )
                total_players = total_players_result.scalars().all()

                all_voted = len(players) == len(total_players)
                self.logger.info("All players voted: %s", all_voted)
            except SQLAlchemyError:
                self.logger.error(
                    "SQLAlchemyError while checking votes for game_id=%s",
                    game_id,
                )
                raise
            except Exception:
                self.logger.error(
                    "Unexpected error while checking votes for game_id=%s",
                    game_id,
                )
                raise
            return all_voted

    async def reset_votes_for_players_in_game(self, game_id: int):
        async with self.app.database.session() as session:
            try:
                query = (
                    update(PlayerModel)
                    .values(votes=0, is_voted=False)
                    .where(PlayerModel.game_id == game_id)
                )
                await session.execute(query)
                await session.commit()
                self.logger.info(
                    "Votes reset successfully for all players in game_id=%s",
                    game_id,
                )
            except SQLAlchemyError:
                await session.rollback()
                self.logger.error(
                    "SQLAlchemyError while resetting votes for game_id=%s",
                    game_id,
                )
                raise
            except Exception:
                await session.rollback()
                self.logger.error(
                    "Unexpected error while resetting votes for game_id=%s",
                    game_id,
                )
                raise
