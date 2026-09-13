from typing import Literal
from uuid import UUID

from app.api.schemas.game import GameResponse
from app.api.schemas.user_actions import Move, Move


class TurnException(Exception): pass
class CellIsFullException(Exception): pass


def update_game(game: GameResponse, move_data: Move) -> GameResponse:
    if not is_user_turn(game.current_turn, move_data.user_uuid, game.player_x_uuid, game.player_o_uuid):
        raise TurnException

    if not is_cell_empty(game.board.data, move_data.col, move_data.row):
        raise CellIsFullException

    game.board.data[move_data.col][move_data.row] = game.current_turn
    game.moves += move_data
    game.current_turn = change_current_turn(game.current_turn)

    winner = get_winner(game.board.data)

    if winner:
        game.status = "finished"
        game.winner = winner

    return game


def is_user_turn(
        current_turn: Literal["X", "O"],
        mover: UUID,
        player_x: UUID,
        player_y: UUID
) -> bool:
    return (
        current_turn == "X" and mover == player_x or
        current_turn == "O" and mover == player_y
    )


def is_cell_empty(
        board: list[list[Literal["X", "O", ""]]],
        col: Literal[0, 1, 2],
        row: Literal[0, 1, 2]
) -> bool:
    return board[col][row] is None


def change_current_turn(current_turn: Literal["X", "O"]) -> Literal["X", "O"]:
    if current_turn == "X":
        return "O"
    else:
        return "X"


def get_winner(board: list[list[Literal["X", "O", ""]]]) -> Literal["X", "O", "draw"] | None:
    for row in board:
        if row[0] == row[1] == row[2] != "":
            return row[0]

    for col in range(3):
        if (board[0][col] == board[1][col] == board[2][col]) and board[0][col] != "":
            return board[0][col]

    if (board[0][0] == board[1][1] == board[2][2]) and board[0][0] != "":
        return board[0][0]
    if (board[0][2] == board[1][1] == board[2][0]) and board[0][2] != "":
        return board[0][2]

    if any(cell == "" for row in board for cell in row):
        return None

    return "draw"

