from fastapi import UploadFile

from src.database_session import DbSession


class ImageUseCase:

    @staticmethod
    def save_image(db_session: DbSession, id, image_data: UploadFile):
        db_session.save_image(image_data, id)
