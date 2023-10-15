FROM python:3.11-alpine

WORKDIR /code
ENV PATH="/root/.local/bin:$PATH"
RUN apk update && apk upgrade && apk add curl openssl \
    && curl -sSL https://install.python-poetry.org | python3 - 
RUN poetry config virtualenvs.create false
RUN openssl req -x509 -newkey rsa:4096 -keyout /etc/ssl/private/key.pem -out /etc/ssl/certs/cert.pem -sha256 -days 3650 -nodes -subj "/CN=localhost"

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
RUN poetry install