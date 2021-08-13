FROM registry.access.redhat.com/ubi8/ubi-minimal:8.4-208

ARG OPA_VERSION

RUN curl -L "https://github.com/open-policy-agent/opa/releases/download/${OPA_VERSION}/opa_linux_amd64" > /usr/bin/opa && \
    chmod +x /usr/bin/opa && opa version

ENTRYPOINT ["/usr/bin/opa"]

CMD ["run"]
