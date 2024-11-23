from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.base.base_accessor import BaseAccessor

from .models import GameModel, GameStatus


class GameAccesor(BaseAccessor):
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
            except IntegrityError:
                await session.rollback()
                raise
            return game

    async def get_last_game(
        self,
        chat_id: int,
    ) -> GameModel:
        async with self.app.database.session() as session:
            query = (
                select(GameModel)
                .where(GameModel.chat_id == chat_id)
                .where(GameModel.status == GameStatus.finished)
            )
            game = await session.execute(query)
            if not game:
                return None
            return game.scalars().first()

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
                return result.scalar_one()
            except IntegrityError:
                await session.rollback()

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
                return result.scalar_one()
            except IntegrityError:
                await session.rollback()

    async def cancel_in_progress_game(
        self,
        chat_id: int,
    ):
        async with self.app.database.session() as session:
            query = (
                update(GameModel)
                .values(status=GameStatus.canceled)
                .where(GameModel.status == GameStatus.in_progress)
            )

            await session.execute(query)
            await session.commit()

    async def get_game_by_chat_id(
        self,
        chat_id: int,
    ):
        async with self.app.database.session() as session:
            query = select(GameModel).where(GameModel.chat_id == chat_id)

            game = await session.execute(query)
            return game.scalars().one()

    async def get_game_by_status(
        self, chat_id: int, status: GameStatus
    ) -> GameModel:
        async with self.app.database.session() as session:
            query = (
                select(GameModel)
                .where(GameModel.chat_id == chat_id)
                .where(GameModel.status == status)
            )

            result = await session.execute(query)
            return result.scalar_one_or_none()
