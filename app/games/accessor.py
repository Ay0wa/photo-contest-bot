from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.base.base_accessor import BaseAccessor

from .models import GameModel


class GameAccesor(BaseAccessor):
    async def create_game(
        self,
        chat_id: int,
        current_round: int = 1,
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
            query = select(GameModel).where(GameModel.chat_id == chat_id)

            game = await session.execute(query)
            return game.scalars().first()

    async def update_current_round(
        self,
        chat_id: int,
        new_round: int,
    ) -> GameModel:
        async with self.app.database.session() as session:
            query = (
                update(GameModel)
                .values(current_round=new_round)
                .where(GameModel.chat_id == chat_id)
                .returning(GameModel)
            )

            try:
                result = await session.execute(query)
                await session.commit()
                return result.scalar_one()
            except IntegrityError:
                await session.rollback()
