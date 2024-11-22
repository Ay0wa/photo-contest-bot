from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.base.base_accessor import BaseAccessor

from .models import ChatModel


class ChatAccesor(BaseAccessor):
    async def create_chat(
        self, chat_id: int, bot_state: str | None = None
    ) -> ChatModel:
        async with self.app.database.session() as session:
            existing_chat = await session.execute(
                select(ChatModel).filter(ChatModel.chat_id == chat_id)
            )
            existing_chat = existing_chat.scalars().first()

            if existing_chat:
                return existing_chat

            chat = ChatModel(chat_id=chat_id, bot_state=bot_state)
            try:
                session.add(chat)
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise
            return chat

    async def update_bot_state(self, chat_id: int, new_state: str) -> ChatModel:
        async with self.app.database.session() as session:
            query = (
                update(ChatModel)
                .values(bot_state=new_state)
                .where(ChatModel.chat_id == chat_id)
                .returning(ChatModel)
            )

            try:
                result = await session.execute(query)
                await session.commit()
                return result.scalar_one()
            except IntegrityError:
                await session.rollback()
                raise

    async def get_by_chat_id(
        self,
        chat_id: int,
    ) -> ChatModel | None:
        async with self.app.database.session() as session:
            query = select(ChatModel).where(ChatModel.chat_id == chat_id)
            try:
                chat = await session.execute(query)
            except IntegrityError:
                await session.rollback()
                raise

            if chat:
                return chat.scalar_one()
            return None
