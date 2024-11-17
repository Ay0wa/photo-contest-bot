from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.games.models import GameModel
from app.store import Store


class TestGameAccessor:

    async def test_create_game(
        self, db_sessionmaker: async_sessionmaker[AsyncSession], store: Store
    ) -> None:
        await store.chats.create_chat(
            chat_id=200000001,
            bot_state="start",
        )
        game = await store.games.create_game(chat_id=200000001)

        assert isinstance(game, GameModel)

        async with db_sessionmaker() as session:
            result = await session.execute(
                select(GameModel).where(GameModel.id == game.id)
            )
            db_game = result.scalar_one_or_none()

        assert db_game is not None
        assert db_game.id == game.id
        assert db_game.chat_id == 200000001
