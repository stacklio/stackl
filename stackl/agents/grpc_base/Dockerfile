FROM python:3.8.2-buster

WORKDIR /usr/src/app

COPY requirements.txt ./


RUN apt-get update && apt-get install -y --no-install-recommends docker.io=18.09.1+dfsg1-7.1+deb10u1 python-dev git gcc build-essential && \
    pip3 install --no-cache-dir -r requirements.txt

# RUN \
#     export REPO_ROOT=/grpc && \
#     git clone -b v1.29.1 https://github.com/grpc/grpc $REPO_ROOT && \
#     cd $REPO_ROOT && \
#     git submodule update --init && \
#     # For the next two commands do `sudo pip install` if you get permissio && \n-denied errors
#     pip install -rrequirements.txt && \
#     GRPC_PYTHON_BUILD_WITH_CYTHON=1 pip install .
#     #&& \
#     #rm -rf /var/lib/apt/lists/*

COPY . .

CMD [ "python3", "-u", "./main.py" ]
