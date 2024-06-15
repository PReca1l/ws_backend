from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, Depends, Form, Path
from typing import Dict, List
import couchdb
import os
import uuid

from src.database_session import get_session, DbSession, CouchDBMessage
from src.imags import ImageUseCase
from src.messages import MessagesUseCase

from config import Config, model


app = FastAPI()

# Dictionary to store connected users {user_id: WebSocket}
connected_users: Dict[str, WebSocket] = {}


# endpoint to receive pictures from http request
@app.post("/upload")
async def create_file(file: UploadFile, id: uuid.UUID = Form(), db_session: DbSession = Depends(get_session)):
    ImageUseCase.save_image(db_session, id, file)
    result, text = model.run(file.file.read())
    return {"file_size": file.size}


@app.get("/history/{username}")
async def get_history(username: str = Path(...), db_session: DbSession = Depends(get_session)) -> List[CouchDBMessage]:
    messages = MessagesUseCase.get_messages(db_session, username)
    return messages


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, db_session: DbSession = Depends(get_session)):
    await websocket.accept()
    connected_users[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            MessagesUseCase.save_message(db_session, data, user_id)
            current_connection = connected_users[user_id]
            await current_connection.send_text(data)

    except WebSocketDisconnect:
        del connected_users[user_id]


@app.on_event("startup")
async def startup_event():
    username = Config.COUCHDB_USER
    password = Config.COUCHDB_PASSWORD
    host = os.getenv("COUCHDB_HOSTNAME", "localhost")

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