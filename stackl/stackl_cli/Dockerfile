FROM busybox:1.31.1 as build

COPY scripts/check-stackl-instance.sh /tmp/check-stackl-instance

RUN wget https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 -O /tmp/jq && \
    chmod a+x /tmp/jq /tmp/check-stackl-instance

FROM python:3.8.1-slim-buster

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY --chown=1001:1001 . /opt/stackl-cli

WORKDIR /opt/stackl-cli

RUN pip3 install --no-cache . && \
    chgrp -R 0 /opt/stackl-cli && \
    chmod -R g=u /opt/stackl-cli

COPY --from=build /tmp/check-stackl-instance /usr/local/bin/check-stackl-instance

COPY --from=build /tmp/jq /usr/local/bin/jq

USER 1001

ENTRYPOINT ["stackl"]

CMD ["--help"]
