import json
from pydantic_core import to_jsonable_python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .models.user import UserORM
from .models.game import GameORM
from .models.base import Base
from ..core.config import settings


engine = create_engine(
    settings.DB_DIRECTORY,
    echo=True,
    json_serializer=lambda obj: json.dumps(obj, default=to_jsonable_python)
)

Base.metadata.create_all(engine)


def get_db():
    with Session(engine) as session:
        return session