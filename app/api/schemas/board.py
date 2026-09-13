from typing import Literal

from pydantic import BaseModel, ConfigDict


class Board(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    data: list[list[Literal["X", "", "O"]]] = [["", "", ""], ["", "", ""], ["", "", ""]]