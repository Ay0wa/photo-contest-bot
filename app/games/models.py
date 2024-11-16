import datetime
from typing import List
from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from app.database.base import BaseModel, created_at

class GameModel(BaseModel):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    current_round: Mapped[int]
    status: Mapped[str]
    created_at: Mapped[created_at]
    finished_at: Mapped[datetime.datetime | None]
    game_time: Mapped[datetime.datetime | None]
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"))
    
    chat: Mapped["ChatModel"] = relationship(
        "ChatModel",
        back_populates="games",
    )
    
    players: Mapped[List["PlayerModel"]] = relationship(
        "PlayerModel",
        back_populates="game", 
        cascade="all, delete-orphan", 
    )
