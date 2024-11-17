import typing

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import BaseModel, created_at

if typing.TYPE_CHECKING:
    from app.games.models import GameModel


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
