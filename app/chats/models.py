from app.database.base import BaseModel, created_at

from typing import List, Optional

from sqlalchemy import ForeignKey, String

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

class ChatModel(BaseModel):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(unique=True)
    bot_state: Mapped[str]
    
    created_at: Mapped[created_at]
    
    games: Mapped[list["GameModel"]] = relationship(
        "GameModel",
        back_populates="chat", 
        cascade="all, delete-orphan",
    )
