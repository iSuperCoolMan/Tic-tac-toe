import random

from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.api.schemas.board import Board
from app.api.schemas.game import GameResponse, Move, GameMessage
from app.database.models.game import GameORM
from app.database.models.user import UserORM


def create_game(db: Session, creator: UUID) -> GameResponse:
    game = GameORM(
        uuid=uuid4(),
        messages=list(),
        moves=list(),
        board=Board(),
        status="waiting",
        current_turn="X",
        created_at=datetime.now()
    )

    is_player_x = random.choice([True, False])

    if is_player_x:
        game.player_x_uuid = creator
    else:
        game.player_o_uuid = creator

    db.add(game)
    db.commit()

    return GameResponse.model_validate(game)


def get_games(db: Session) -> GameResponse:
    statement = select(GameORM)
    games = db.scalars(statement).all()

    return [GameResponse.model_validate(game) for game in games]


def get_game_by_uuid(db: Session, uuid: UUID) -> GameResponse:
    statement = select(GameORM).where(GameORM.uuid == uuid)
    game = db.scalars(statement).one_or_none()

    return GameResponse.model_validate(game)


def update_game_by_uuid_after_user_connection(
        db: Session,
        game_uuid: UUID,
        user_uuid: UUID
) -> GameResponse | None:
    statement = select(GameORM).where(GameORM.uuid == game_uuid)
    game = db.scalars(statement).one_or_none()

    if game.player_x_uuid is None and game.player_o_uuid != user_uuid:
        game.player_x_uuid = user_uuid
    elif game.player_o_uuid is None and game.player_x_uuid != user_uuid:
        game.player_o_uuid = user_uuid
    else:
        return None

    game.status = "playing"

    db.commit()

    return GameResponse.model_validate(game)


def update_game_in_db(db: Session, updated_game: GameResponse):
    updated_data = updated_game.model_dump(exclude_unset=True)

    statement = update(GameORM).where(GameORM.uuid == updated_game.uuid).values(**updated_data)
    game = db.scalars(statement).one_or_none()

    db.execute(statement)
    db.commit()

    return GameResponse.model_validate(game)


def update_game_by_uuid_after_message(db: Session, uuid: UUID, message: GameMessage) -> GameResponse:
    game = db.query(GameORM).get(uuid)
    game.messages = [*game.messages, message]

    db.commit()

    return GameResponse.model_validate(game)
