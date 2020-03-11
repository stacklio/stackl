FROM nexus-dockerext.dome.dev/ubi8/ubi-minimal:8.0 as build

COPY scripts/check-stackl-instance.sh /tmp/check-stackl-instance

RUN curl -L https://nexus.dome.dev/repository/github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 > /tmp/jq && \
    chmod a+x /tmp/jq /tmp/check-stackl-instance

FROM nexus-dockerext.dome.dev/ubi8/ubi-minimal:8.0
# version 8.1 is not working currently, see https://github.com/redhat-discovery/discovery/issues/228

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY nexus.repo /etc/yum.repos.d/nexus.repo
COPY pip.conf /etc/pip.conf
COPY required-packages required-packages

RUN rm /etc/yum.repos.d/ubi.repo && \
    while IFS= read -r package; do microdnf -y install "$package"; done < required-packages && \
    microdnf clean all

COPY . /opt/stackl-cli

WORKDIR /opt/stackl-cli

RUN pip3 install --no-cache .

COPY --from=build /tmp/check-stackl-instance /usr/local/bin/check-stackl-instance
COPY --from=build /tmp/jq /usr/local/bin/jq

USER 1001

ENTRYPOINT ["stackl"]

CMD ["--help"]
