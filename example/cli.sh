#!/bin/sh

set -e
case "$1" in

  # Seed Redis with dummy data...
  setup)
    echo "Pushing data to redis..."
    redis-cli -h $REDIS_HOST -n 1 SET mykey0 myval0 > /dev/null
    redis-cli -h $REDIS_HOST -n 1 SET mykey1 myval1 > /dev/null
    redis-cli -h $REDIS_HOST -n 1 SET mykey2 myval2 > /dev/null
    redis-cli -h $REDIS_HOST -n 1 KEYS '*'
    ;;

  # Query Redis and write to the S3 location saved in the S3_PREFIX ENV var
  *)
    echo "Feching $* from $REDIS_HOST..."
    redis-cli -h $REDIS_HOST -n 1 GET $*
    ;;
esac
