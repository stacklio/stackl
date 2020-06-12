FROM python:3.8.2-slim-buster

COPY requirements_worker.txt requirements_worker.txt

RUN pip3 install --no-cache-dir -r requirements_worker.txt && \
    mkdir /opt/stackl

COPY . /opt/stackl

CMD ["python", "/opt/stackl/workers/worker.py"]
