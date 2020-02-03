#Example of a comment
FROM python:3.6-alpine3.8
RUN pip3 install websockets
COPY . /agent
WORKDIR /agent
EXPOSE 8889
CMD ["python", "agent.py"]
