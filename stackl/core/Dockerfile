FROM registry.access.redhat.com/ubi8/ubi-minimal:8.2-349


ENV PYTHONFAULTHANDLER=1 \
  MODULE_NAME="core.main" \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.9

# System deps:
RUN microdnf install -y python38 gcc python38-devel make && \
    pip3 install --no-cache-dir "poetry==$POETRY_VERSION"&& \
    microdnf clean all

COPY stackl/core/start.sh /start.sh
RUN chmod +x /start.sh

COPY stackl/core/gunicorn_conf.py /gunicorn_conf.py

COPY stackl/core/start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

# Copy only requirements to cache them in docker layer
WORKDIR /app

COPY stackl/core/. /app
ENV PYTHONPATH=/app

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

EXPOSE 8080

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Uvicorn
CMD ["/start.sh"]
