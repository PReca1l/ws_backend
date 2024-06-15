import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import UploadFile
from pydantic import BaseModel
import couchdb
import os

from config import Config


class CouchDBMessage(BaseModel):
    id: str
    message: str
    user_id: str
    attachment_url: str
    timestamp: Optional[str] = None


def _get_couchdb():
    username = Config.COUCHDB_USER
    password = Config.COUCHDB_PASSWORD
    host = Config.COUCHDB_HOSTNAME

    couch = couchdb.Server(url=f'http://{username}:{password}@{host}:5984/')

    return couch


class DbSession:
    def __init__(self):
        self.couch = _get_couchdb()


    def get_messages(self, username: str) -> List[CouchDBMessage]:
        db = self.couch["application"]
        messages = []
        docs = db.find(
            {
                "selector": {
                    "user_id": username
                },
                "fields": ["_id", "message", "user_id", "_attachments", "timestamp"],
            }
        )
        for doc in docs:
            if "_attachments" in doc:
                for attachment_name in doc["_attachments"]:
                    host = Config.COUCHDB_SERVER
                    db_name = Config.COUCHDB_DATABASE
                    attachment_url = f"{host}/{db_name}/{doc['_id']}/{attachment_name}"
                    message = CouchDBMessage(
                        id=doc["_id"],
                        message=doc["message"],
                        user_id=doc["user_id"],
                        attachment_url=attachment_url,
                        timestamp=doc["timestamp"],
                    )
                    messages.append(message)
        return messages

    def save_image(self, file: bytes, image_id: uuid.UUID, filename):
        couch = _get_couchdb()
        db = couch["application"]
        image_id = str(image_id)

        if image_id in db:
            doc = db[image_id]
        else:
            doc = {
                "_id": str(image_id),
            }
            db.save(doc)

        db.put_attachment(doc, file, filename)

        return str(image_id)

    def save_message(self, message_id: uuid.UUID, message: str, user_id):
        couch = _get_couchdb()
        db = couch["application"]
        message_id = str(message_id)
        current_time = datetime.now().isoformat()

        if message_id in db:
            doc = db[message_id]
            doc["message"] = message
            doc["user_id"] = user_id
            doc["timestamp"] = current_time
        else:
            doc = {
                "_id": message_id,
                "message": message,
                "user_id": user_id,
                "timestamp": current_time,
            }

        db.save(doc)


def get_session():
    couch = DbSession()

    return couch
