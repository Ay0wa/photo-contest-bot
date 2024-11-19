from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.players.models import PlayerModel
from app.store import Store


class TestGameAccessor:
    async def test_create_game(
        self, db_sessionmaker: async_sessionmaker[AsyncSession], store: Store
    ) -> None:
        await store.chats.create_chat(chat_id=200000001, bot_state="start")
        game = await store.games.create_game(chat_id=200000001)
        player = await store.players.create_player(
            username="test_username",
            avatar_url="test_avatar_url",
            game_id=game.id,
        )

        assert isinstance(player, PlayerModel)

        async with db_sessionmaker() as session:
            result = await session.execute(
                select(PlayerModel).where(PlayerModel.id == player.id)
            )
            db_player = result.scalar_one_or_none()

        assert db_player is not None
        assert db_player.id == player.id
        assert db_player.game_id == game.id
