import asyncio
from contextlib import ExitStack
from json import JSONDecodeError
from uuid import UUID

from starlette.testclient import TestClient, WebSocketTestSession

from app.api.main import app
from app.api.schemas.game import GameResponse
from app.api.schemas.user import UserCreate, Token
from app.core.security import get_user_uuid
from tests.integration.test_websocket import send_message, choose_random_player, random_action, listen
from tests.unit.test_auth import try_register, login
from tests.unit.test_game_logic import print_data, get_validated_data
from tests.unit.test_games import get_games, create_game, connect_to_the_game, get_game_websocket
from tests.utils.string_generator import random_string


client = TestClient(app)

user1 = UserCreate(username="user1", password="password", email="email1@test.com")
user2 = UserCreate(username="user2", password="password", email="email2@test.com")
user3 = UserCreate(username="user3", password="password", email="email3@test.com")
random_user = UserCreate(username=random_string(6), password="password", email=f"{random_string(6)}@test.com")

try_register(client, user1)
try_register(client, user2)
try_register(client, user3)
random_user_registered = try_register(client, random_user)

if not random_user_registered: raise Exception(random_user.model_dump())

token1 = login(client, user1)
token2 = login(client, user2)
token3 = login(client, user3)
token4 = login(client, random_user)


def set_game(player1_token: Token, player2_token: Token):
    player1_uuid = get_user_uuid(player1_token.access_token)
    player2_uuid = get_user_uuid(player2_token.access_token)

    games = get_games(client)

    uuids = [game.player_o_uuid for game in games] + [game.player_x_uuid for game in games]

    if uuids and player1_uuid in uuids:
        game = [
            game for game in games if
            game.player_o_uuid == player1_uuid or
            game.player_x_uuid == player1_uuid
        ][0]
    else:
        game = create_game(client, player1_token)

    if not (game.player_o_uuid == player2_uuid or game.player_x_uuid == player2_uuid):
        connect_to_the_game(client, game.uuid, player2_token)

    return game


def playing(game: GameResponse, player1_token: Token, player2_token: Token, *viewers: Token):
    with ExitStack() as stack:
        player1_ws = stack.enter_context(get_game_websocket(client, game.uuid, player1_token))
        player2_ws = stack.enter_context(get_game_websocket(client, game.uuid, player2_token))

        viewers_ws = []

        for viewer_token in viewers:
            ws = stack.enter_context(get_game_websocket(client, game.uuid, viewer_token))
            viewers_ws.append(ws)

        for viewer_ws in viewers_ws:
            send_message(viewer_ws, "Хорошей игры!")


        async def action():
            while True:
                player = choose_random_player(player1_ws, player2_ws)
                random_action(player)


        async def handle_data():
            nonlocal game

            while game.status != "finished":
                data = await listen(player1_ws, player2_ws, *viewers_ws)
                validated_data = get_validated_data(data)
                print_data(validated_data, game.player_x_uuid, game.player_o_uuid)

                if isinstance(data, GameResponse):
                    game = GameResponse.model_validate(data)

            print(f"Game over! Winner - {game.winner}")


        asyncio.gather(action(), handle_data())


game1 = set_game(token1, token3)

playing(game1, token1, token3, token2, token4)

# game2 = set_game(user2.uuid, token2, random_user.uuid, token4)




