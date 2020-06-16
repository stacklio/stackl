FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7-2020-04-27


ENV PYTHONFAULTHANDLER=1 \
  MODULE_NAME="rest.main" \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.9

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

COPY library /library

# Copy only requirements to cache them in docker layer
WORKDIR /app

COPY stackl/rest/poetry.lock stackl/rest/pyproject.toml /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY stackl/rest/. /app