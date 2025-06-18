from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.chats.models import ChatModel
from app.store import Store


class TestChatAccessor:
    async def test_create_chat(
        self, db_sessionmaker: async_sessionmaker[AsyncSession], store: Store
    ) -> None:
        chat = await store.chats.get_or_create_chat(
            chat_id=200000001,
        )

        assert isinstance(chat, ChatModel)

        async with db_sessionmaker() as session:
            result = await session.execute(
                select(ChatModel).where(ChatModel.chat_id == chat.chat_id)
            )
            db_chat = result.scalar_one_or_none()

        assert db_chat is not None
        assert db_chat.chat_id == chat.chat_id
        assert db_chat.chat_id == 200000001

    async def test_get_by_chat_id(
        self, db_sessionmaker: async_sessionmaker[AsyncSession], store: Store
    ) -> None:
        await store.chats.get_or_create_chat(
            chat_id=200000001,
        )

        chat = await store.chats.get_by_chat_id(
            chat_id=200000001,
        )

        assert isinstance(chat, ChatModel)

        async with db_sessionmaker() as session:
            result = await session.execute(
                select(ChatModel).where(ChatModel.chat_id == chat.chat_id)
            )
            db_chat = result.scalar_one_or_none()

        assert db_chat is not None
        assert db_chat.chat_id == chat.chat_id
        assert db_chat.chat_id == 200000001
