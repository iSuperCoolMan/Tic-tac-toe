from contextlib import contextmanager
from uuid import UUID

from starlette.testclient import TestClient, WebSocketTestSession

from app.api.schemas.game import GameResponse
from app.api.schemas.user import Token


def create_game(client: TestClient, token: Token) -> GameResponse:
    headers = {"Authorization": f"{token.token_type.capitalize()} {token.access_token}"}
    response = client.post("/games", headers=headers)

    print(response.status_code)
    print(response.json())

    if response.status_code == 200:
        return GameResponse.model_validate(response.json())
    else:
        raise Exception


def get_games(client: TestClient) -> list[GameResponse]:
    response = client.get("/games")

    if response.status_code == 200:
        return [GameResponse.model_validate(game) for game in response.json()]
    else:
        raise Exception


def connect_to_the_game(client: TestClient, game_uuid: UUID, user_token: Token) -> GameResponse:
    headers = {"Authorization": f"{user_token.token_type.capitalize()} {user_token.access_token}"}
    response = client.post(f"/games/{game_uuid}/join", headers=headers)

    if response.status_code == 200:
        return GameResponse.model_validate(response.json()["Connection"])
    else:
        raise Exception


@contextmanager
def get_game_websocket(client: TestClient, game_uuid: UUID, user_token: Token) -> WebSocketTestSession:
    headers = {"Authorization": f"{user_token.token_type.capitalize()} {user_token.access_token}"}

    with client.websocket_connect(f"games/ws/{game_uuid}", headers=headers) as websocket:
        yield websocket