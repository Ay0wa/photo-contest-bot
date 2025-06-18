from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.players.models import PlayerModel
from app.store import Store


class TestGameAccessor:
    async def test_create_player(
        self, db_sessionmaker: async_sessionmaker[AsyncSession], store: Store
    ) -> None:
        await store.chats.get_or_create_chat(chat_id=200000001)
        game = await store.games.create_game(chat_id=200000001)
        player = await store.players.create_player(
            user_id=3231223,
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

    async def test_get_player_by_id(
        self, db_sessionmaker: async_sessionmaker[AsyncSession], store: Store
    ) -> None:
        await store.chats.get_or_create_chat(chat_id=200000001)
        game = await store.games.create_game(chat_id=200000001)
        player = await store.players.create_player(
            user_id=3231223,
            username="test_username",
            avatar_url="test_avatar_url",
            game_id=game.id,
        )
        player = await store.players.get_player_by_id(
            player_id=player.id,
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
