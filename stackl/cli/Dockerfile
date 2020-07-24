FROM registry.access.redhat.com/ubi8/ubi-minimal:8.2-301 as build

COPY --chown=1001:0 . /opt/stackl-cli

WORKDIR /opt/stackl-cli

ENV PATH="/opt/venv/bin:$PATH"

RUN microdnf install -y python38 && \
    python3 -m venv /opt/venv && \
    pip3 install --no-cache .

COPY scripts/check-stackl-instance.sh /tmp/stackl-cli/bin/check-stackl-instance
COPY scripts/docker-entrypoint.sh /tmp/stackl-cli/bin/docker-entrypoint.sh
COPY scripts/convert_json_from_spec.py /tmp/stackl-cli/bin/convert_json_from_spec

RUN curl -L https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 > /tmp/jq && \
    chmod a+x /tmp/jq /tmp/stackl-cli/bin/check-stackl-instance /tmp/stackl-cli/bin/docker-entrypoint.sh /tmp/stackl-cli/bin/convert_json_from_spec && \
    mkdir -p /tmp/stackl-cli/.stackl && \
    chgrp -R 0 /tmp/stackl-cli && \
    chmod -R g=u /tmp/stackl-cli

FROM registry.access.redhat.com/ubi8/ubi-minimal:8.2-301

COPY --from=build /opt/venv /opt/venv
COPY --from=build /tmp/stackl-cli /opt/stackl-cli
COPY --from=build /tmp/jq /usr/local/bin/jq

WORKDIR /opt/stackl-cli

ENV PATH="/opt/venv/bin:/opt/stackl-cli/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV HOME=/opt/stackl-cli

USER 1001:0

# ENTRYPOINT ["/opt/stackl-cli/bin/docker-entrypoint.sh", "stackl"]

# CMD ["--help"]
