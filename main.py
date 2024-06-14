from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict

app = FastAPI()

# Dictionary to store connected users {user_id: WebSocket}
connected_users: Dict[str, WebSocket] = {}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    connected_users[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            # Process and broadcast the message
            await broadcast(f"{user_id}: {data}")

    except WebSocketDisconnect:
        del connected_users[user_id]

async def broadcast(message: str):
    for connection in connected_users.values():
        await connection.send_text(message)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)