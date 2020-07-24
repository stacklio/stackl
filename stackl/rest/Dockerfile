FROM registry.access.redhat.com/ubi8/ubi-minimal:8.2-339


ENV PYTHONFAULTHANDLER=1 \
  MODULE_NAME="rest.main" \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.9

# System deps:
RUN microdnf install -y python38 && \
    pip3 install --no-cache-dir "poetry==$POETRY_VERSION"&& \
    microdnf clean all

COPY stackl/rest/start.sh /start.sh
RUN chmod +x /start.sh

COPY stackl/rest/gunicorn_conf.py /gunicorn_conf.py

COPY stackl/rest/start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

COPY library /library

# Copy only requirements to cache them in docker layer
WORKDIR /app

COPY stackl/rest/poetry.lock stackl/rest/pyproject.toml /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY stackl/rest/. /app
ENV PYTHONPATH=/app
EXPOSE 80

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Uvicorn
CMD ["/start.sh"]
