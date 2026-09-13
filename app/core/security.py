import asyncio

from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from starlette import status

from app.core.config import settings


denylist = set()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.TOKEN_SECRET_KEY,
        algorithm=settings.TOKEN_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict[str: str]:
    try:
        payload = jwt.decode(token, settings.TOKEN_SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен"
        )


def get_user_uuid(token: str = Depends(oauth2_scheme)) -> UUID:
    user_data = decode_token(token)
    return UUID(user_data["sub"])


def get_expire_delta_from_token(token: Annotated[str, Depends(oauth2_scheme)]) -> datetime:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        expire = payload.get("exp")

        if expire is None:
            raise credentials_exception
    except:
        raise credentials_exception

    return expire - datetime.now().timestamp()


async def revoke_access_token(token: Annotated[str, Depends(oauth2_scheme)]) -> None:
    delta = get_expire_delta_from_token(token)

    denylist.add(token)
    await asyncio.sleep(delta)
    denylist.remove(token)

