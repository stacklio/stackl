FROM python:3.8.1-buster as build

COPY --chown=1001:0 . /opt/stackl-cli

WORKDIR /opt/stackl-cli

ENV PATH="/opt/venv/bin:$PATH"

RUN python -m venv /opt/venv && \
    pip3 install --no-cache .

COPY scripts/check-stackl-instance.sh /tmp/stackl-cli/bin/check-stackl-instance

RUN wget https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 -O /tmp/jq && \
    chmod a+x /tmp/jq /tmp/stackl-cli/bin/check-stackl-instance && \
    mkdir -p /opt/stackl-cli/.stackl && \
    chgrp -R 0 /tmp/stackl-cli && \
    chmod -R g=u /tmp/stackl-cli

FROM python:3.8.1-slim-buster

RUN apt-get update && \
    apt-get install -y --no-install-recommends libyaml-dev=0.2.1-1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


COPY --from=build /opt/venv /opt/venv
COPY --from=build /tmp/stackl-cli /opt/stackl-cli
COPY --from=build /tmp/jq /usr/local/bin/jq

WORKDIR /opt/stackl-cli

ENV PATH="/opt/venv/bin:/opt/stackl-cli/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# USER 1001

ENTRYPOINT ["stackl"]

CMD ["--help"]
