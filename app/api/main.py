from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.auth import router as auth_router
from .routers.games import router as games_router


app = FastAPI(
    title="Tic-tac-toe API",
    openapi_prefix="/api"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Не рекомендуется в продакшене
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")
app.include_router(games_router, prefix="/games")
