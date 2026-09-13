from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from sqlalchemy import DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.api.schemas.board import Board
from app.api.schemas.game import GameMessage, Move
from app.database.models.base import Base


class GameORM(Base):
    __tablename__ = "games"

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    messages: Mapped[list[GameMessage]] = mapped_column(JSON)
    moves: Mapped[list[Move]] = mapped_column(JSON)
    board: Mapped[Board] = mapped_column(JSON, default=lambda: Board().model_dump())
    status: Mapped[Literal["waiting", "playing", "finished"]] = mapped_column()
    current_turn: Mapped[Literal["X", "O"]] = mapped_column()
    winner: Mapped[Optional[Literal["X", "O", "draw"]]] = mapped_column(nullable=True)
    player_x_uuid: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    player_o_uuid: Mapped[Optional[UUID]] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )