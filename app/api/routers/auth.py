from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from ..schemas.user import UserCreate, UserResponse, Token
from app.database.crud.user import get_user_by_username, get_user_by_email, create_user
from app.core.security import verify_password, create_access_token, revoke_access_token, oauth2_scheme


router = APIRouter(
    tags=["auth"],
    responses={
        401: {"description": "Не авторизован"},
        400: {"description": "Неверный запрос"},
    }
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
        user_data: UserCreate,
        db: Session = Depends(get_db)
):
    existing_user = get_user_by_username(db, username=user_data.username)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )

    existing_email = get_user_by_email(db, email=user_data.email)

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    new_user = create_user(db, user_data)

    return new_user


@router.post(
    "/login",
    response_model=Token
)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = get_user_by_username(db, username=form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.uuid)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/exit")
async def logout(background_tasks: BackgroundTasks, access_token = Annotated[str, Depends(oauth2_scheme)]):
    background_tasks.add_task(revoke_access_token, access_token)

    return {
        "Message": "Logout successfully"
    }
