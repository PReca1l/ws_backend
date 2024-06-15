FROM python:3.11
# generate fastapi dockerfile
RUN pip install poetry
# copy the app folder to the container
COPY . /app
WORKDIR /app
RUN poetry export -f requirements.txt > requirements.txt
RUN pip install -r requirements.txt
# expose the port 8000
CMD python main.py