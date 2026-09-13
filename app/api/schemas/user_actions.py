from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserAction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_uuid: UUID
    created_at: datetime = Field(default_factory=datetime.now)


class GameMessage(UserAction):
    text: str


class Move(UserAction):
    row: Literal[0, 1, 2]
    col: Literal[0, 1, 2]