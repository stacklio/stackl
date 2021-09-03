FROM registry.access.redhat.com/ubi8/ubi-minimal:8.4-208

RUN curl https://download.redis.io/releases/redis-6.2.5.tar.gz -O && \ 
      microdnf install tar gzip logrotate shadow-utils systemd gcc make && \
      tar zxf redis-6.2.5.tar.gz && cd redis-6.2.5 && make MALLOC=libc

COPY redis.conf /usr/local/etc/redis/redis.conf

CMD ["./src/redis-server", "/usr/local/etc/redis/redis.conf", "--appendonly", "yes"]
