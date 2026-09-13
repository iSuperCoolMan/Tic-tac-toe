import json
import datetime
from typing import Any
from uuid import UUID, uuid4

from app.api.schemas.board import Board
from app.api.schemas.game import GameResponse
from app.api.schemas.user_actions import GameMessage


def print_data(data, player_x_uuid: UUID, player_o_uuid: UUID):
    if isinstance(data, GameMessage):
        print_message(data, player_x_uuid, player_o_uuid)
    elif isinstance(data, GameResponse):
        print_game_data(data)
    else:
        print(data)


def print_game_data(data):
    str1 = (data.board.data[0] + '{:>40}').format('right aligned') + f"current turn: {data.current_turn}"
    str2 = (data.board.data[1] + '{:>40}').format('right aligned') + f"status: {data.status}"
    str3 = (data.board.data[2] + '{:>40}').format('right aligned') + f"winner: {data.winner}"

    print(str1)
    print(str2)
    print(str3)
    print()


def print_message(data, player_x_uuid: UUID, player_o_uuid: UUID):
    if data.user_uuid == player_x_uuid:
        log_message = "player X: -"
    elif data.user_uuid == player_o_uuid:
        log_message = "player O: -"
    else:
        log_message = "Viewer: -"

    print(log_message + data.text)


def get_validated_data(data) -> GameResponse | GameMessage | Any:
    if not data.startswith("\"{"):
        data = {"text": data}
    else:
        data = json.loads(json.loads(data))

    if not data.keys() - GameResponse.model_fields.keys():
        return GameResponse.model_validate(data)
    elif not data.keys() - GameMessage.model_fields.keys():
        return GameMessage.model_validate(data)
    else:
        return data


# data = GameMessage(
#     user_uuid=uuid4(),
#     text="test",
#     created_at=datetime.datetime.now()
# ).model_dump()
#
# print(data)
# print(not data.keys() - GameMessage.model_fields.keys())
# print(data.keys() - GameMessage.model_fields.keys())