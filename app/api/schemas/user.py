from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
import re


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


    @classmethod
    @field_validator("password")
    def password_must_be_strong(cls, value):
        if len(value) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        return value


    @classmethod
    @field_validator("username")
    def username_must_be_valid(cls, value):
        if not re.match(r"^[a-zA-Z0-9_]{3,20}$", value):
            raise ValueError(
                "Имя пользователя: 3-20 символов, только буквы, цифры и _"
            )
        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    username: str
    email: str
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
