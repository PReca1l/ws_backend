# Welding defects detector backend

This is the backend of the welding defects detector project. It is a REST API that receives an image of a welding and returns the detected defects.
This solution uses couchdb for data storage
# Configuration

First, there is two .env files. The one for backend and the other for 
cdn_emulator.

.env for cdn_emulator looks as follows
```
COUCHDB_USER=admin
COUCHDB_PASSWORD=password
COUCHDB_HOST=http://localhost:5984
COUCHDB_HOSTNAME=localhost
COUCHDB_DATABASE=application
MODEL_PATH=./models
```

IMAGE_CDN is cdn address where images are stored
PREDICT_URL points to model deployment location

.env for backend looks as follows
```
IMAGE_CDN=http://cdn:8002
COUCHDB_USER=admin
COUCHDB_PASSWORD=password
COUCHDB_HOST=http://couchdb:5984
COUCHDB_HOSTNAME=localhost
COUCHDB_DATABASE=application
PREDICT_URL=http://host.docker.internal:8881/predict
```

# Deployment

```bash
docker compose up --build
```