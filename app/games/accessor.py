from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.base.base_accessor import BaseAccessor

from .models import GameModel, GameStatus


class GameAccessor(BaseAccessor):
    async def create_game(
        self,
        chat_id: int,
        current_round: int = 0,
    ) -> GameModel:
        async with self.app.database.session() as session:
            game = GameModel(chat_id=chat_id, current_round=current_round)
            try:
                session.add(game)
                await session.commit()
                self.logger.info("Game created successfully")
            except IntegrityError:
                await session.rollback()
                self.logger.error("IntegrityError during game creation")
                raise
            except SQLAlchemyError:
                await session.rollback()
                self.logger.error("SQLAlchemyError during game creation")
                raise
            except Exception:
                await session.rollback()
                self.logger.error("Unexpected error during game creation")
                raise
            return game

    async def get_game_by_id(
        self,
        game_id: int,
    ) -> GameModel:
        async with self.app.database.session() as session:
            try:
                query = select(GameModel).where(GameModel.id == game_id)
                result = await session.execute(query)
                game = result.scalars().one()
                self.logger.info("Game retrieved successfully by game_id")
            except IntegrityError:
                await session.rollback()
                self.logger.error(
                    "IntegrityError during game retrieval by game_id"
                )
                raise
            except SQLAlchemyError:
                self.logger.error(
                    "SQLAlchemyError during game retrieval by game_id"
                )
                raise
            except Exception:
                self.logger.error(
                    "Unexpected error during game retrieval by game_id"
                )
                raise
            return game

    async def get_last_game(self, chat_id: int) -> GameModel | None:
        async with self.app.database.session() as session:
            try:
                query = (
                    select(GameModel)
                    .where(GameModel.chat_id == chat_id)
                    .where(GameModel.status == GameStatus.finished)
                    .order_by(GameModel.id.desc())
                )
                result = await session.execute(query)
                game = result.scalars().first()

                if game:
                    self.logger.info(
                        "Last finished game retrieved successfully",
                    )
                else:
                    self.logger.warning("No finished games found")
            except SQLAlchemyError:
                self.logger.error(
                    "SQLAlchemyError while retrieving the last finished game",
                )
                raise
            except Exception:
                self.logger.error(
                    "Unexpected error while retrieving the last finished game",
                )
                raise
            return game

    async def get_game_by_chat_id(
        self,
        chat_id: int,
    ) -> GameModel:
        async with self.app.database.session() as session:
            try:
                query = select(GameModel).where(GameModel.chat_id == chat_id)
                result = await session.execute(query)
                game = result.scalars().one()
                self.logger.info("Game retrieved successfully by chat_id")
            except IntegrityError:
                await session.rollback()
                self.logger.error(
                    "IntegrityError during game retrieval by chat_id"
                )
                raise
            except SQLAlchemyError:
                self.logger.error(
                    "SQLAlchemyError during game retrieval by chat_id"
                )
                raise
            except Exception:
                self.logger.error(
                    "Unexpected error during game retrieval by chat_id"
                )
                raise
            return game

    async def get_game_by_status(
        self,
        chat_id: int,
        status: GameStatus,
    ) -> GameModel | None:
        async with self.app.database.session() as session:
            try:
                query = (
                    select(GameModel)
                    .where(GameModel.chat_id == chat_id)
                    .where(GameModel.status == status)
                )
                result = await session.execute(query)
                game = result.scalar_one_or_none()
                if game:
                    self.logger.info("Game retrieved successfully by status")
                else:
                    self.logger.warning(
                        "No game found for chat_id=%s with status=%s",
                        chat_id,
                        status,
                    )
            except SQLAlchemyError:
                self.logger.error(
                    "SQLAlchemyError during game retrieval by status"
                )
                raise
            except Exception:
                self.logger.error(
                    "Unexpected error during game retrieval by status"
                )
                raise
            return game

    async def list_games(self) -> list[GameModel]:
        async with self.app.database.session() as session:
            try:
                query = select(GameModel)
                result = await session.execute(query)
                games = result.scalars().all()
                self.logger.info("Games retrieved successfully")
            except SQLAlchemyError:
                self.logger.error("SQLAlchemyError during games listing")
                raise
            except Exception:
                self.logger.error("Unexpected error during games listing")
                raise
            return games

    async def get_games_by_filters(self, filters: dict):
        async with self.app.database.session() as session:
            try:
                query = select(GameModel)

                if "chat_id" in filters:
                    query = query.where(GameModel.chat_id == filters["chat_id"])

                if "status" in filters:
                    query = query.where(GameModel.status == filters["status"])

                if "current_round" in filters:
                    query = query.where(
                        GameModel.current_round == filters["current_round"]
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

    async def update_game_status(
        self,
        game_id: int,
        new_status: GameStatus,
    ) -> GameModel:
        async with self.app.database.session() as session:
            query = (
                update(GameModel)
                .values(status=new_status)
                .where(GameModel.id == game_id)
                .returning(GameModel)
            )
            try:
                result = await session.execute(query)
                await session.commit()
                self.logger.info("Game status updated successfully")
                return result.scalar_one()
            except IntegrityError:
                await session.rollback()
                self.logger.error("IntegrityError during game status update")
                raise
            except SQLAlchemyError:
                await session.rollback()
                self.logger.error("SQLAlchemyError during game status update")
                raise
            except Exception:
                await session.rollback()
                self.logger.error("Unexpected error during game status update")
                raise

    async def update_current_round(
        self,
        game_id: int,
    ) -> GameModel:
        async with self.app.database.session() as session:
            query = (
                update(GameModel)
                .values(current_round=GameModel.current_round + 1)
                .where(GameModel.id == game_id)
                .returning(GameModel)
            )
            try:
                result = await session.execute(query)
                await session.commit()
                self.logger.info("Game round updated successfully")
                return result.scalar_one()
            except IntegrityError:
                await session.rollback()
                self.logger.error("IntegrityError during game round update")
                raise
            except SQLAlchemyError:
                await session.rollback()
                self.logger.error("SQLAlchemyError during game round update")
                raise
            except Exception:
                await session.rollback()
                self.logger.error("Unexpected error during game round update")
                raise

    async def cancel_in_progress_game(
        self,
        chat_id: int,
    ):
        async with self.app.database.session() as session:
            query = (
                update(GameModel)
                .values(status=GameStatus.canceled)
                .where(GameModel.status == GameStatus.in_progress)
                .where(GameModel.chat_id == chat_id)
            )
            try:
                await session.execute(query)
                await session.commit()
                self.logger.info("In-progress game canceled successfully")
            except SQLAlchemyError:
                await session.rollback()
                self.logger.error(
                    "SQLAlchemyError during canceling in-progress game"
                )
                raise
            except Exception:
                await session.rollback()
                self.logger.error(
                    "Unexpected error during canceling in-progress game"
                )
                raise
