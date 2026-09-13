from fastapi.testclient import TestClient

from app.api.schemas.user import UserCreate, UserResponse, Token


def try_register(client: TestClient, user_data: UserCreate) -> UserResponse | None:
    response = client.post("/auth/register", json=user_data.model_dump())

    if response.status_code == 201:
        return UserResponse.model_validate(response.json())
    elif (
            response.status_code == 400 and
            response.json() == {'detail': 'Пользователь с таким именем уже существует'}
        ):
        return None
    else:
        raise Exception


def login(client: TestClient, user_data: UserCreate) -> Token:
    correct_data = {"username": user_data.username, "password": user_data.password}
    response = client.post("/auth/login", data=correct_data)

    if response.status_code == 200:
        return Token.model_validate(response.json())
    else:
        raise Exception