import os

from fastapi import FastAPI, Response
from couchdb import Server
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

username = os.getenv("COUCHDB_USER")
password = os.getenv("COUCHDB_PASSWORD")
server = Server(f"http://{username}:{password}@localhost:5984/")


@app.get("/{image_id}/{filename}")
async def get_image(image_id: str, filename: str):
    db = server["application"]
    doc = db[image_id]
    attachment = db.get_attachment(doc, filename)
    return Response(content=attachment.read(), media_type="image/png")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
