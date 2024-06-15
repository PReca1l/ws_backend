from typing import Optional

from fastapi import UploadFile

from src.database_session import DbSession


class ImageUseCase:

    @staticmethod
    def save_image(db_session: DbSession, id, image_data: UploadFile | bytes, filename: Optional[str] = None):
        if hasattr(image_data, "filename"):
            return db_session.save_image(image_data.file.read(), id, image_data.filename)
        else:
            return db_session.save_image(image_data, id, filename)
