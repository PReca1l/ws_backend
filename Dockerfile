FROM python:3.11 as base
# generate fastapi dockerfile
RUN pip install poetry
RUN poetry export -f requirements.txt > requirements.txt
RUN pip install -r requirements.txt

FROM base as final
# copy the app folder to the container
COPY . /app
WORKDIR /app

# expose the port 8000
CMD python main.py