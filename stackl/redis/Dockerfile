FROM registry.access.redhat.com/ubi8/ubi-minimal:8.2-345

COPY CentOS-AppStream.repo /etc/yum.repos.d/CentOS-AppStream.repo
COPY RPM-GPG-KEY-centosofficial /etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial

RUN microdnf install -y redis-5.0.3-2.module_el8.2.0+318+3d7e67ea && redis-server --version

COPY redis.conf /usr/local/etc/redis/redis.conf

CMD ["redis-server", "/usr/local/etc/redis/redis.conf", "--appendonly", "yes"]
