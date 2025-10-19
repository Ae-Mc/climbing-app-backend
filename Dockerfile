FROM python:3.12-alpine

WORKDIR /code
RUN apk add git
RUN pip install uv

COPY pyproject.toml pyproject.toml
RUN uv sync --no-dev
ENTRYPOINT [ "uv", "run", "--link-mode=copy", "climbing" ]
