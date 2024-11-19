import typing

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import BaseModel, created_at

if typing.TYPE_CHECKING:
    from app.games.models import GameModel

from enum import StrEnum, auto


class ChatStatus(StrEnum):
    init = auto()
    idle = auto()
    start_new_game = auto()
    round_processing = auto()
    game_processing = auto()
    game_finished = auto()


class ChatModel(BaseModel):
    __tablename__ = "chats"

    chat_id: Mapped[int] = mapped_column(primary_key=True)

    bot_state: Mapped[str] = mapped_column(server_default="init")

    created_at: Mapped[created_at]

    games: Mapped[list["GameModel"]] = relationship(
        "GameModel",
        back_populates="chat",
        cascade="all, delete-orphan",
    )
