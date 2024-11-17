from sqlalchemy.exc import IntegrityError

from app.base.base_accessor import BaseAccessor

from .models import ChatModel


class ChatAccesor(BaseAccessor):
    async def create_chat(self, chat_id: str, bot_state: str) -> ChatModel:
        async with self.app.database.session() as session:
            chat = ChatModel(chat_id=chat_id, bot_state=bot_state)
            session.add(chat)
            try:
                await session.commit()
                return chat
            except IntegrityError:
                await session.rollback()
