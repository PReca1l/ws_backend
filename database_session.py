import uuid
from typing import List

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


def _get_couchdb():
    username = os.getenv("COUCHDB_USER")
    password = os.getenv("COUCHDB_PASSWORD")
    host = os.getenv("COUCHDB_HOSTNAME", "localhost")

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
                "fields": ["_id", "message", "user_id", "_attachments"],
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
                    )
                    messages.append(message)
        return messages

    def save_image(self, file: UploadFile, image_id: uuid.UUID):
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

        db.put_attachment(doc, file.file.read(), file.filename)

        return str(image_id)

    def save_message(self, message_id: uuid.UUID, message: str, user_id):
        couch = _get_couchdb()
        db = couch["application"]
        message_id = str(message_id)

        if message_id in db:
            doc = db[message_id]
            doc["message"] = message
            doc["user_id"] = user_id
        else:
            doc = {
                "_id": message_id,
                "message": message,
                "user_id": user_id
            }

        db.save(doc)


def get_session():
    couch = DbSession()

    return couch
