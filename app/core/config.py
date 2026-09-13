import os

from typing import Any

from pydantic import BaseModel


class Settings(BaseModel):
    DB_DIRECTORY: str = "sqlite:///app/database/database.db"
    TOKEN_SECRET_KEY: str = os.getenv("TOKEN_SECRET_KEY")
    TOKEN_ALGORITHM: str = os.getenv("TOKEN_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


    def __init__(self, /, **data: Any):
        super().__init__(**data)

        kwargs = self.__dict__
        null_kwargs = []

        for key in kwargs:
            if not kwargs[key]:
                null_kwargs.append(key)

        if null_kwargs:
            raise ValueError(f"{null_kwargs} cannot be null.")


settings = Settings()
