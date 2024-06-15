import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    COUCHDB_SERVER = os.getenv('COUCHDB_HOST', 'http://localhost:5984')
    COUCHDB_DATABASE = os.getenv('COUCHDB_DATABASE', 'application')
    COUCHDB_USER = os.getenv('COUCHDB_USER', 'admin')
    COUCHDB_PASSWORD = os.getenv('COUCHDB_PASSWORD', 'admin')
    COUCHDB_HOSTNAME = os.getenv('COUCHDB_HOSTNAME', 'localhost')