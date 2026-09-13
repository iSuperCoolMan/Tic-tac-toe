from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.database.database import get_db
from ..schemas.game import GameResponse, Move, GameMessage
from ..schemas.user_actions import GameMessage, Move
from ..websocket.game_handler import manager
from app.database.crud.game import (
    get_games,
    create_game,
    update_game_by_uuid_after_user_connection,
    get_game_by_uuid,
    update_game_by_uuid_after_message, update_game_in_db
)
from app.core.security import get_user_uuid
from ..websocket.security import get_token_from_websocket
from ...utils.game_logic import update_game, TurnException, CellIsFullException

router = APIRouter(tags=["games"])


@router.get("/", response_model=list[GameResponse])
async def games_list(db: Session = Depends(get_db)):
    games = get_games(db)
    return games


@router.post("/", response_model=GameResponse)
async def post_new_game(
        db: Session = Depends(get_db),
        creator_uuid: UUID = Depends(get_user_uuid)
):
    new_game = create_game(db, creator_uuid)
    return new_game


@router.post("/{game_uuid}/join")
async def connect_to_the_game(
        game_uuid: UUID,
        db: Session = Depends(get_db),
        user_uuid: UUID = Depends(get_user_uuid)
):
    connection = update_game_by_uuid_after_user_connection(db, game_uuid, user_uuid)

    if connection:
        return {"Connection": connection, "Message": "Connected successfully"}
    else:
        return {"Connection": connection, "Message": "Not connected"}


@router.websocket("/ws/{game_uuid}")
async def game_websocket(
        websocket: WebSocket,
        game_uuid: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(get_token_from_websocket)
):
    user_uuid = get_user_uuid(token)
    game = get_game_by_uuid(db, game_uuid)

    non_player = False

    await manager.connect(game_uuid, user_uuid, websocket)

    if not (game.player_o_uuid == user_uuid or game.player_x_uuid == user_uuid):
        non_player = True

    for message in game.messages:
        await websocket.send_json(message.model_dump_json())

    for move in game.moves:
        await websocket.send_json(move.model_dump_json())


    async def handle_data_after_move(move: Move):
        nonlocal game

        if non_player:
            await websocket.send_text("Вы не можете делать ходы, вы не игрок")
            return

        try:
            game_data = update_game(game, move)
            game = update_game_in_db(db, game_data)
            await manager.broadcast(game_uuid, game)
        except TurnException:
            await websocket.send_text("Дождитесь своей очереди")
        except CellIsFullException:
            await websocket.send_text("Клетка уже занята, выберите другую")


    async def handle_data_after_message(message: GameMessage):
        update_game_by_uuid_after_message(db, game_uuid, message)
        await manager.broadcast(game_uuid, message)


    async def produce():
        while True:
            data = await manager.get_validated_data(game_uuid, user_uuid)

            if isinstance(data, Move):
                await manager.add_task_to(game_uuid, await handle_data_after_move(data))
            elif isinstance(data, GameMessage):
                await manager.add_task_to(game_uuid, await handle_data_after_message(data))
            else:
                raise TypeError(data)


    try:
        await produce()
    except WebSocketDisconnect:
        manager.disconnect(game_uuid, user_uuid)
        return
    except Exception as e:
        print(e)
        print(e.__traceback__)
        raise

