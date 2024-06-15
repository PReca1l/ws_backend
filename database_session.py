import uuid

from fastapi import UploadFile
import couchdb
import os


def _get_couchdb():
    username = os.getenv("COUCHDB_USER")
    password = os.getenv("COUCHDB_PASSWORD")
    host = os.getenv("COUCHDB_HOST")

    couch = couchdb.Server(url=f'http://{username}:{password}@{host}:5984/')

    return couch


class DbSession:
    def __init__(self):
        self.couch = _get_couchdb()

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

    def save_message(self, message_id: uuid.UUID, message: str):
        couch = _get_couchdb()
        db = couch["application"]
        message_id = str(message_id)

        if message_id in db:
            doc = db[message_id]
            doc["message"] = message
        else:
            doc = {
                "_id": message_id,
                "message": message
            }

        db.save(doc)


def get_session():
    couch = DbSession()

    return couch
