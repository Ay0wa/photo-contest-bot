from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.base.base_accessor import BaseAccessor

from .models import ChatModel


class ChatAccessor(BaseAccessor):
    async def get_or_create_chat(
        self, chat_id: int, bot_state: str | None = None
    ) -> ChatModel:
        async with self.app.database.session() as session:
            existing_chat = await session.execute(
                select(ChatModel).filter(ChatModel.chat_id == chat_id)
            )
            existing_chat = existing_chat.scalars().first()

            if existing_chat:
                self.logger.info("Existing chat found successfully")
                return existing_chat

            chat = ChatModel(chat_id=chat_id, bot_state=bot_state)
            session.add(chat)
            await session.commit()
            self.logger.info("New chat created successfully")
            return chat

    async def get_by_chat_id(self, chat_id: int) -> ChatModel | None:
        async with self.app.database.session() as session:
            query = select(ChatModel).where(ChatModel.chat_id == chat_id)
            result = await session.execute(query)
            chat = result.scalars().first()
            if chat:
                self.logger.info("Chat retrieved successfully by chat_id")
            else:
                self.logger.warning("No chat found for chat_id=%s", chat_id)
            return chat

    async def list_chats(self) -> list[ChatModel] | None:
        async with self.app.database.session() as session:
            try:
                query = select(ChatModel)
                result = await session.execute(query)
                chats = result.scalars().all()
                if chats:
                    self.logger.info("Chats retrieved successfully")
                else:
                    self.logger.warning("No chats found in the database")
            except SQLAlchemyError:
                self.logger.error(
                    "SQLAlchemyError occurred while listing chats"
                )
                raise
            except Exception:
                self.logger.error(
                    "Unexpected error occurred while listing chats"
                )
                raise
            return chats

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
                self.logger.info(
                    "Bot state updated successfully for chat_id=%s", chat_id
                )
                return result.scalar_one()
            except IntegrityError:
                await session.rollback()
                self.logger.error(
                    "IntegrityError occurred while updating bot state"
                )
                raise
            except SQLAlchemyError:
                await session.rollback()
                self.logger.error(
                    "SQLAlchemyError occurred while updating bot state"
                )
                raise
            except Exception:
                await session.rollback()
                self.logger.error(
                    "Unexpected error occurred while updating bot state"
                )
                raise
