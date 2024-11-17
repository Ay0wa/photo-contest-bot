from sqlalchemy.exc import IntegrityError

from app.base.base_accessor import BaseAccessor

from .models import PlayerModel


class PlayerAccesor(BaseAccessor):
    async def create_player(
        self, username: str, avatar_url: str, game_id: int
    ) -> PlayerModel:
        async with self.app.database.session() as session:
            player = PlayerModel(
                username=username, avatar_url=avatar_url, game_id=game_id
            )
            session.add(player)
            try:
                await session.commit()
                return player
            except IntegrityError:
                await session.rollback()
