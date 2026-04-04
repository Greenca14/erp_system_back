#!/bin/sh
cat <<EOF > /usr/local/etc/redis/users.acl
user default off
user ${REDIS_USER:?REDIS_USER is not defined} on >${REDIS_PASSWORD:?REDIS_PASSWORD is not defined} ~* &* +@all
EOF

exec redis-server /usr/local/etc/redis/redis.conf