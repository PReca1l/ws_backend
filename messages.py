import json
import uuid

from pydantic import BaseModel

from database_session import DbSession


class Message(BaseModel):
    id: uuid.UUID
    text: str
    username: str


class MessagesUseCase:

    @staticmethod
    def save_message(db_session: DbSession, message: str, user_id: str):
        data = json.loads(message)
        message = Message(**data)
        db_session.save_message(message.id, message.text, user_id)


    @staticmethod
    def get_messages(db_session: DbSession, username: str):
        messages = db_session.get_messages(username)
        return messages
