FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim-2020-04-27


ENV PYTHONFAULTHANDLER=1 \
  MODULE_NAME="rest.main" \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.9

# System deps:
RUN pip install "poetry==1.0.8"

# Copy only requirements to cache them in docker layer
WORKDIR /app

COPY poetry.lock pyproject.toml /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY . /app