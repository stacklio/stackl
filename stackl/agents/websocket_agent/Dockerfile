FROM python:3.8.1-slim-buster

WORKDIR /agent

RUN pip3 install --no-cache-dir websockets==8.1

COPY . /agent

EXPOSE 8889

CMD ["python", "agent.py"]
