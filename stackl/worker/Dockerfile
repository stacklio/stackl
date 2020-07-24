FROM registry.access.redhat.com/ubi8/ubi-minimal:8.2-345

ENV PYTHONFAULTHANDLER=1 \
  MODULE_NAME="job.main" \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.9

# System deps:
RUN microdnf install -y python38 && \
    pip3 install --no-cache-dir "poetry==$POETRY_VERSION" && \
    microdnf clean all

COPY library /library

# Copy only requirements to cache them in docker layer
WORKDIR /app

COPY stackl/worker/poetry.lock stackl/worker/pyproject.toml /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY stackl/worker/. /app

CMD ["poetry", "run", "start-worker"]
