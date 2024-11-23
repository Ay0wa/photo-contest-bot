from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.chats.models import ChatModel
from app.store import Store


class TestChatAccessor:
    async def test_create_chat(
        self, db_sessionmaker: async_sessionmaker[AsyncSession], store: Store
    ) -> None:
        chat = await store.chats.create_chat(
            chat_id=200000001,
            bot_state="init",
        )

        assert isinstance(chat, ChatModel)

        async with db_sessionmaker() as session:
            result = await session.execute(
                select(ChatModel).where(ChatModel.id == chat.id)
            )
            db_chat = result.scalar_one_or_none()

        assert db_chat is not None
        assert db_chat.id == chat.id
        assert db_chat.chat_id == 200000001
