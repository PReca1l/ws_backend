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

# Deployment through docker-compose

```bash
docker compose up --build
```

# Manual deployment

### Step one

Deploy the machine learning service by 
following instructions in the README.md file there: https://github.com/PReca1l/ws_model

### Step two

Launch couchdb using docker

```bash
docker compose up -d --build couchdb
```

Create databases "application" and "_users" in GUI at http://yourdestination:5984/_utils/
Use credentials from docker compose to log in to the GUI

### Step three

Launch the CDN emulator

First, installation of venv is needed:
```bash
sudo apt install -y python3
sudo apt install -y python3-venv
```

Then, create a virtual environment and install the required packages
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install poetry
poetry install
```

Finally, go to the cdn_emulator directory:
```bash
cd cdn_emulator
python main.py
```

### Step four
Launch the backend
Since every dependency is set up, the only thing left is to run the backend itself


```bash
source venv/bin/activate
python main.py
```