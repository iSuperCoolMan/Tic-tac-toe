import random
import asyncio

from starlette.testclient import WebSocketTestSession

from tests.utils.string_generator import random_string


async def listen(*listeners: WebSocketTestSession) -> dict:
    data = await asyncio.gather([listener.receive_text() for listener in listeners])
    return data[0]


def send_message(websocket: WebSocketTestSession, text: str):
    websocket.send_text(text)


def send_move(websocket: WebSocketTestSession, row: int, col: int):
    websocket.send_json({"row": row, "col": col})


def choose_random_player(player1: WebSocketTestSession, player2: WebSocketTestSession) -> WebSocketTestSession:
    return random.choice([player1, player2])


def random_action(player: WebSocketTestSession):
    move = random.choice([True, False])

    if move:
        row, col = random.choices([0, 1, 2], k=2)
        send_move(player, row, col)
    else:
        send_message(player, random_string(10))