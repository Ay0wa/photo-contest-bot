from sqlalchemy import select, update
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

            try:
                session.add(player)
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise
            return player

    async def get_players_by_id(self, game_id: int) -> list[PlayerModel]:
        async with self.app.database.session() as session:
            query = select(PlayerModel).where(PlayerModel.game_id == game_id)

            result = await session.execute(query)
            return result.scalars().all()

    async def update_round(self, player_id: int, new_round: int) -> PlayerModel:
        async with self.app.database.session() as session:
            query = (
                update(PlayerModel)
                .values(round=new_round)
                .where(PlayerModel.id == player_id)
                .returning(PlayerModel)
            )

            try:
                result = await session.execute(query)
                await session.commit()
            except IntegrityError:
                await session.rollback()
            return result.scalar_one()

    async def get_players_by_round(self, current_round: int, game_id: int):
        async with self.app.database.session() as session:
            query = select(PlayerModel).where(
                PlayerModel.game_id == game_id
                and PlayerModel.round == current_round
            )

            result = await session.execute(query)
            return result.scalars().all()
