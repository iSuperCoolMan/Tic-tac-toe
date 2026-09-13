from datetime import datetime
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.api.schemas.board import Board
from app.api.schemas.user_actions import UserAction, GameMessage, Move


class GameResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    messages: list[GameMessage]
    moves: list[Move]
    board: Board
    status: Literal["waiting", "playing", "finished"]
    current_turn: Literal["X", "O"]
    winner: Optional[Literal["X", "O", "draw"]]
    player_x_uuid: Optional[UUID]
    player_o_uuid: Optional[UUID]
    created_at: datetime
