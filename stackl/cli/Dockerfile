FROM registry.access.redhat.com/ubi8/ubi-minimal:8.2-345

COPY --chown=1001:0 . /opt/stackl-cli

WORKDIR /opt/stackl-cli

ENV PATH="/opt/venv/bin:$PATH"

RUN microdnf install -y python38 && \
    python3 -m venv /opt/venv && \
    pip3 install --no-cache .

COPY scripts/check-stackl-instance.py /opt/stackl-cli/bin/check-stackl-instance
COPY scripts/docker-entrypoint.sh /opt/stackl-cli/bin/docker-entrypoint.sh
COPY scripts/convert_json_from_spec.py /opt/stackl-cli/bin/convert_json_from_spec

RUN curl -L https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 > /opt/jq && \
    chmod a+x /opt/jq /opt/stackl-cli/bin/check-stackl-instance /opt/stackl-cli/bin/docker-entrypoint.sh /opt/stackl-cli/bin/convert_json_from_spec && \
    mkdir -p /opt/stackl-cli/.stackl && \
    chgrp -R 0 /opt/stackl-cli && \
    chmod -R g=u /opt/stackl-cli

WORKDIR /opt/stackl-cli

ENV PATH="/opt/venv/bin:/opt/stackl-cli/bin:/opt:$PATH"
ENV PYTHONUNBUFFERED=1
ENV HOME=/opt/stackl-cli

USER 1001:0

# CMD ["--help"]
