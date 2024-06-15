import json
import uuid

from pydantic import BaseModel

from database_session import DbSession


class Message(BaseModel):
    id: uuid.UUID
    text: str


class MessagesUseCase:

    @staticmethod
    def save_message(db_session: DbSession, message: str):
        print(message)
        data = json.loads(message)
        message = Message(**data)
        db_session.save_message(message.id, message.text)
