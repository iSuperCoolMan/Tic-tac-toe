from starlette import status
from starlette.websockets import WebSocket


async def get_token_from_websocket(websocket: WebSocket) -> str:
    auth_header = websocket.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None

    return auth_header.split(" ")[1]