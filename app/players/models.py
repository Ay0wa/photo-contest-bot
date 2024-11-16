from app.database.base import BaseModel, created_at

from typing import List, Optional

from sqlalchemy import ForeignKey, String

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

class PlayerModel(BaseModel):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    username: Mapped[str]
    avatar_url: Mapped[str]
    
    status: Mapped[str]
    created_at: Mapped[created_at]
    
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"))
    
    game: Mapped["GameModel"] = relationship(
        "GameModel", 
        back_populates="players"
    )