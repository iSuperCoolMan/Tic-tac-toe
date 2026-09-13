import asyncio
import json
from asyncio import Task
from dataclasses import dataclass, field
from typing import Coroutine
from uuid import UUID, uuid4

from starlette.websockets import WebSocket

from app.api.schemas.game import GameResponse
from app.api.schemas.user_actions import Move, GameMessage


@dataclass
class GameSession:
    game_uuid: UUID
    tasks_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    connections: dict[UUID: WebSocket] = field(default_factory=dict)

    _consumer_task: Task = None


    async def _consume(self):
        try:
            while True:
                await self.tasks_queue.get()
                self.tasks_queue.task_done()
        except asyncio.CancelledError:
            while self.tasks_queue.qsize() > 0:
                await self.tasks_queue.get()
                self.tasks_queue.task_done()


    async def add_task(self, task: Coroutine):
        await self.tasks_queue.put(task)


    def connect(self, user_uuid: UUID, websocket: WebSocket):
        if not self.connections:
            if not self._consumer_task:
                self._consumer_task = asyncio.create_task(self._consume())
            else:
                raise ValueError

        self.connections[user_uuid] = websocket


    def disconnect(self, user_uuid: UUID):
        self.connections.pop(user_uuid)

        if not self.connections:
            if self._consumer_task:
                self._consumer_task.cancel()
                self._consumer_task = None
            else:
                raise ValueError


class ConnectionManager:
    sessions: dict[UUID: GameSession]


    def __init__(self):
        self.sessions: dict[UUID: GameSession] = {}


    async def connect(self, game_uuid: UUID, user_uuid: UUID, websocket: WebSocket):
        await websocket.accept()

        if game_uuid not in self.sessions:
            self.sessions[game_uuid] = GameSession(game_uuid)

        self.sessions[game_uuid].connect(user_uuid, websocket)


    def add_task_to(self, game_uuid: UUID, task: Coroutine):
        self.sessions[game_uuid].add_task(task)


    def disconnect(self, game_uuid: UUID, user_uuid: UUID):
        if game_uuid in self.sessions:
            self.sessions[game_uuid].disconnect(user_uuid)

            if not self.sessions[game_uuid].connections:
                self.sessions.pop(game_uuid)


    async def broadcast(self, game_uuid: UUID, data: GameMessage | GameResponse):
        if game_uuid not in self.sessions:
            return

        for user_id, websocket in self.sessions[game_uuid].connections.items():
            try:
                await websocket.send_json(data.model_dump_json())
            except Exception:
                self.disconnect(game_uuid, user_id)


    async def get_validated_data(self, game_uuid: UUID, user_uuid: UUID) -> GameMessage | Move:
        websocket = self.sessions[game_uuid].connections[user_uuid]

        data = await websocket.receive_text()

        if not data.startswith("{"):
            data = {"text": data}
        else:
            data = json.loads(data)

        data["user_uuid"] = user_uuid

        if not data.keys() - Move.model_fields.keys():
            return Move.model_validate(data)
        elif not data.keys() - GameMessage.model_fields.keys():
            return GameMessage.model_validate(data)
        else:
            raise ValueError(data)


manager = ConnectionManager()
