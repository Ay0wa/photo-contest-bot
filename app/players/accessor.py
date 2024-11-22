from sqlalchemy import or_, select, update
from sqlalchemy.exc import IntegrityError

from app.base.base_accessor import BaseAccessor

from .models import PlayerModel, PlayerStatus


class PlayerAccesor(BaseAccessor):
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
            except IntegrityError as e:
                await session.rollback()
                self.logger.error(f"IntegrityError при создании игрока: {e}")
                raise
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Ошибка при создании игрока: {e}")
                raise

    async def get_players_by_game_id(self, game_id: int) -> list[PlayerModel]:
        async with self.app.database.session() as session:
            try:
                query = select(PlayerModel).where(
                    PlayerModel.game_id == game_id
                )
                result = await session.execute(query)
                return result.scalars().all()
            except Exception as e:
                self.logger.error(
                    f"Ошибка при получении игроков по game_id: {e}"
                )
                return []

    async def get_player_by_user_id(
        self, game_id: int, user_id: int
    ) -> PlayerModel:
        async with self.app.database.session() as session:
            try:
                query = (
                    select(PlayerModel)
                    .where(PlayerModel.user_id == user_id)
                    .where(PlayerModel.game_id == game_id)
                )
                result = await session.execute(query)
                return result.scalars().first()
            except Exception as e:
                self.logger.error(
                    f"Ошибка при получении игроков по game_id и user_id: {e}"
                )
                return None

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
                return result.scalars().all()
            except Exception as e:
                self.logger.error(
                    f"Ошибка при получении игроков в текущем раунде: {e}"
                )
                return []

    async def get_player_with_max_votes(self, game_id: int) -> PlayerModel | None:
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
                if not player:
                    self.logger.info(
                        f"Игроки с голосами в игре {game_id} не найдены."
                    )
                else:
                    self.logger.info(
                        f"""Игрок с максимальным количеством голосов в игре
                        {game_id}: {player.username},
                        голоса: {player.votes}"""
                    )
                return player
            except Exception as e:
                self.logger.error(
                    f"""Ошибка при получении игрока 
                    с максимальным количеством голосов: {e}"""
                )
                return None

    async def get_player_with_min_votes(self, game_id: int):
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
                if not player:
                    self.logger.info(
                        f"Игроки с голосами в игре {game_id} не найдены."
                    )
                else:
                    self.logger.info(
                        f"""Игрок с минимальным количеством голосов в игре 
                        {game_id}: {player.username}, голоса: {player.votes}"""
                    )
                return player
            except Exception as e:
                self.logger.error(
                    f"Ошибка при получении игрока с минимальным количеством голосов: {e}"
                )
                return None

    async def get_player_by_status(self, game_id: int, status: PlayerStatus):
        async with self.app.database.session() as session:
            try:
                query = select(PlayerModel).where(
                    (PlayerModel.game_id == game_id)
                    & (PlayerModel.status == status)
                )
                result = await session.execute(query)
                return result.scalars().one_or_none()
            except Exception as e:
                self.logger.error(
                    f"Ошибка при получении игроков по статусу: {e}"
                )
                return None

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
                return result.scalar_one()
            except IntegrityError as e:
                await session.rollback()
                self.logger.error(f"IntegrityError при обновлении раунда: {e}")
                raise
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Ошибка при обновлении раунда: {e}")
                raise

    async def update_voted(self, game_id: int, player_id: int, new_voted: bool):
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
                return result.scalar_one()
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Ошибка при обновлении is_voted: {e}")
                raise

    async def update_votes_by_username(self, username: str, game_id: int):
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
                return result.scalar_one()
            except Exception as e:
                await session.rollback()
                self.logger.error(
                    f"Ошибка при обновлении голосов по имени пользователя: {e}"
                )
                raise

    async def update_players_status(self, game_id: int, player_ids: list[int]):
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

                return result.scalars().all()

            except Exception as e:
                await session.rollback()
                self.logger.error(f"Ошибка при обновлении статуса: {e}")
                raise

    async def update_player_status(
        self, game_id: int, player_id: int, status: PlayerStatus
    ):
        async with self.app.database.session() as session:
            try:
                query = (
                    update(PlayerModel)
                    .where(
                        PlayerModel.id == player_id
                        and PlayerModel.game_id == game_id
                    )
                    .values(status=status)
                )

                await session.execute(query)
                await session.commit()
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Ошибка при обновлении статуса: {e}")
                raise

    async def check_all_votes_true_for_game(self, game_id: int):
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
                    .where(PlayerModel.is_voted == True)
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

                return len(players) == len(total_players)
            except Exception as e:
                self.logger.error(
                    f"Ошибка при проверке проголосовавших участников: {e}"
                )
                raise

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
                return True
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Ошибка при сброса голосов: {e}")
                return False
