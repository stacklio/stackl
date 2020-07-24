FROM registry.access.redhat.com/ubi8/ubi-minimal:8.2-345

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt

RUN microdnf install -y python38 && \
  pip3 install --no-cache-dir -r requirements.txt

COPY main.py .

ENTRYPOINT [ "python", "main.py" ]
