import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, Depends, Form, Path
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from pydantic import BaseModel
import couchdb
import os
import uuid
import httpx
import base64

from src.database_session import get_session, DbSession, CouchDBMessage
from src.imags import ImageUseCase
from src.messages import MessagesUseCase

from config import Config


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dictionary to store connected users {user_id: WebSocket}
connected_users: Dict[str, WebSocket] = {}


class UploadResponseModel(BaseModel):
    report: str
    img: str

# endpoint to receive pictures from http request
@app.post("/upload")
async def create_file(
        file: UploadFile,
        username: str = Form(),
        id: uuid.UUID = Form(),
        db_session: DbSession = Depends(get_session)
) -> UploadResponseModel:
    ImageUseCase.save_image(db_session, id, file)
    async with httpx.AsyncClient() as client:
        response = await client.post(f"http://localhost:8881/predict", files={"file": file.file})

    json_response = response.json()
    decoded_image = base64.decodebytes(bytes(json_response["img"], "utf-8"))
    report_data = json_response["report"]
    image_id = ImageUseCase.save_image(db_session, id, decoded_image, "result_" + file.filename)
    host = Config.COUCHDB_SERVER
    db_name = Config.COUCHDB_DATABASE
    attachment_url = f"{host}/{db_name}/{image_id}/result_{file.filename}"

    current_connection = connected_users[username]
    ws_response = {
        "username": "server",
        "text": report_data,
        "previewImage": attachment_url,
        "id": str(id)
    }
    response_as_text = json.dumps(ws_response)
    await current_connection.send_text(response_as_text)
    return UploadResponseModel(report=report_data, img=json_response["img"])


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