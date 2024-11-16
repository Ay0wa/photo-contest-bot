from sqlalchemy.exc import IntegrityError
from app.base.base_accessor import BaseAccessor

from .models import GameModel

from sqlalchemy import select

class GameAccesor(BaseAccessor):
    async def create_game(self, chat_id: int, ) -> GameModel:
        async with self.app.database.session() as session:
            game = GameModel(chat_id=chat_id)
            session.add(game)
            try:
                await session.commit()
                return game
            except IntegrityError:
                await session.rollback()
    