FROM python:3.8.2-slim-buster as build

COPY --chown=1001:0 . /opt/stackl-cli

WORKDIR /opt/stackl-cli

ENV PATH="/opt/venv/bin:$PATH"

RUN python -m venv /opt/venv && \
    pip3 install --no-cache . && \
    apt-get update && \
    apt-get install -y --no-install-recommends wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY scripts/check-stackl-instance.sh /tmp/stackl-cli/bin/check-stackl-instance
COPY scripts/docker-entrypoint.sh /tmp/stackl-cli/bin/docker-entrypoint.sh
COPY scripts/convert_json_from_spec.py /tmp/stackl-cli/bin/convert_json_from_spec

RUN wget -q https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 -O /tmp/jq && \
    chmod a+x /tmp/jq /tmp/stackl-cli/bin/check-stackl-instance /tmp/stackl-cli/bin/docker-entrypoint.sh /tmp/stackl-cli/bin/convert_json_from_spec && \
    mkdir -p /tmp/stackl-cli/.stackl && \
    chgrp -R 0 /tmp/stackl-cli && \
    chmod -R g=u /tmp/stackl-cli && \
    chmod g=u /etc/passwd

FROM python:3.8.2-slim-buster

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
ENV HOME=/opt/stackl-cli

USER 1001:0

ENTRYPOINT ["/opt/stackl-cli/bin/docker-entrypoint.sh", "stackl"]

CMD ["--help"]
