FROM registry.access.redhat.com/ubi8/ubi-minimal:8.2-345

ENV PYTHONFAULTHANDLER=1 \
  MODULE_NAME="agent.main" \
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

# Copy only requirements to cache them in docker layer
WORKDIR /app

COPY stackl/agent/poetry.lock stackl/agent/pyproject.toml /app/


# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY stackl/agent/. /app

CMD ["arq", "agent.main.AgentSettings"]