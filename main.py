from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, Depends, Form
from typing import Dict
import couchdb
import os
import uuid

from dotenv import load_dotenv

from database_session import get_session, DbSession
from imags import ImageUseCase
from messages import MessagesUseCase

load_dotenv()
app = FastAPI()

# Dictionary to store connected users {user_id: WebSocket}
connected_users: Dict[str, WebSocket] = {}


# endpoint to receive pictures from http request
@app.post("/upload")
async def create_file(file: UploadFile, id: uuid.UUID = Form(), db_session: DbSession = Depends(get_session)):
    print(f"Received file of size {file.size}")
    ImageUseCase.save_image(db_session, id, file)
    return {"file_size": file.size}


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, db_session: DbSession = Depends(get_session)):
    await websocket.accept()
    connected_users[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            MessagesUseCase.save_message(db_session, data)
            await broadcast(f"{user_id}: {data}")

    except WebSocketDisconnect:
        del connected_users[user_id]

async def broadcast(message: str):
    for connection in connected_users.values():
        await connection.send_text(message)


@app.on_event("startup")
async def startup_event():
    username = os.getenv("COUCHDB_USER")
    password = os.getenv("COUCHDB_PASSWORD")
    host = os.getenv("COUCHDB_HOST")

    couch = couchdb.Server(url=f'http://{username}:{password}@{host}:5984/')

    db_names = (
        "_users",
        "application"
    )

    for db_name in db_names:
        if db_name not in couch:
            couch.create(db_name)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)