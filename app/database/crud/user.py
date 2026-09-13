from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash
from app.database.models.user import UserORM


def create_user(db: Session, user_data: UserCreate) -> UserResponse:
    user = UserORM(
        uuid=uuid4(),
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )

    db.add(user)
    db.commit()

    return UserResponse.model_validate(user)


def get_user_by_uuid(db: Session, uuid: UUID) -> UserResponse | None:
    statement = select(UserORM).where(UserORM.uuid == uuid)
    user = db.scalars(statement).one_or_none()

    if user:
        return UserResponse.model_validate(user)
    else:
        return None


def get_user_by_email(db: Session, email: str) -> UserResponse:
    statement = select(UserORM).where(UserORM.email == email)
    user = db.scalars(statement).one_or_none()

    if user:
        return UserResponse.model_validate(user)
    else:
        return None


def get_user_by_username(db: Session, username: str) -> UserResponse:
    statement = select(UserORM).where(UserORM.username == username)
    user = db.scalars(statement).one_or_none()

    if user:
        return UserResponse.model_validate(user)
    else:
        return None


