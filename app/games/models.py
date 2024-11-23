import datetime
import typing
from enum import StrEnum, auto
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel, created_at

if typing.TYPE_CHECKING:
    from app.chats.models import ChatModel
    from app.players.models import PlayerModel


class GameStatus(StrEnum):
    in_progress = auto()
    finished = auto()
    canceled = auto()


class GameModel(BaseModel):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)

    current_round: Mapped[Optional[int]]  # noqa: UP007
    status: Mapped[GameStatus] = mapped_column(
        default=GameStatus.in_progress,
        server_default=GameStatus.in_progress,
    )

    created_at: Mapped[created_at]
    finished_at: Mapped[Optional[datetime.datetime]]  # noqa: UP007
    game_time: Mapped[Optional[datetime.datetime]]  # noqa: UP007

    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.chat_id", ondelete="CASCADE")
    )

    chat: Mapped["ChatModel"] = relationship(
        "ChatModel",
        back_populates="games",
    )

    players: Mapped[list["PlayerModel"]] = relationship(
        "PlayerModel",
        back_populates="game",
        cascade="all, delete-orphan",
    )
