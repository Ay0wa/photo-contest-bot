import typing
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import BaseModel, created_at

if typing.TYPE_CHECKING:
    from app.games.models import GameModel


class PlayerModel(BaseModel):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str]
    avatar_url: Mapped[str]

    status: Mapped[Optional[str]]
    created_at: Mapped[created_at]

    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"),
    )

    game: Mapped["GameModel"] = relationship(
        "GameModel",
        back_populates="players",
    )
