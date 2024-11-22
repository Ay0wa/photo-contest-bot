import typing
from enum import StrEnum, auto
from typing import Optional

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel, created_at

if typing.TYPE_CHECKING:
    from app.games.models import GameModel


class PlayerStatus(StrEnum):
    winner = auto()
    loser = auto()
    in_game = auto()
    voting = auto()


class PlayerModel(BaseModel):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int]

    username: Mapped[str]
    avatar_url: Mapped[str]
    round: Mapped[int] = mapped_column(server_default="1")

    votes: Mapped[int] = mapped_column(
        server_default="0",
    )
    is_voted: Mapped[bool] = mapped_column(
        Boolean,
        server_default="FALSE",
    )

    status: Mapped[PlayerStatus] = mapped_column(
        default=PlayerStatus.voting,
        server_default=PlayerStatus.voting,
    )
    created_at: Mapped[created_at]

    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"),
    )

    game: Mapped["GameModel"] = relationship(
        "GameModel",
        back_populates="players",
    )
