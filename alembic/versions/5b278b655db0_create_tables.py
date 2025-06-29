"""create tables

Revision ID: 5b278b655db0
Revises: 
Create Date: 2024-11-24 01:12:32.630701

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5b278b655db0"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "chats",
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column(
            "bot_state",
            sa.Enum(
                "init",
                "idle",
                "start_new_game",
                "round_processing",
                "game_processing",
                "game_finished",
                name="chatstate",
            ),
            server_default="init",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('utc', now())"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("chat_id"),
    )
    op.create_table(
        "games",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("current_round", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("in_progress", "finished", "canceled", name="gamestatus"),
            server_default="in_progress",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('utc', now())"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("game_time", sa.DateTime(), nullable=True),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["chat_id"], ["chats.chat_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("avatar_url", sa.String(), nullable=False),
        sa.Column("round", sa.Integer(), server_default="1", nullable=False),
        sa.Column("votes", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "is_voted", sa.Boolean(), server_default="FALSE", nullable=False
        ),
        sa.Column(
            "status",
            sa.Enum(
                "winner", "loser", "in_game", "voting", name="playerstatus"
            ),
            server_default="voting",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("TIMEZONE('utc', now())"),
            nullable=False,
        ),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("players")
    op.drop_table("games")
    op.drop_table("chats")
    op.drop_table("admins")
    # ### end Alembic commands ###
