#!bin/sh

set -e
case "$1" in
  setup)
    echo "Pushing data to redis..."
    redis-cli -h redis -n 1 SET mykey0 myval0 > /dev/null
    redis-cli -h redis -n 1 SET mykey1 myval1 > /dev/null
    redis-cli -h redis -n 1 SET mykey2 myval2 > /dev/null
    redis-cli -h redis -n 1 KEYS '*'
    ;;
  *)
    redis-cli -h redis -n 1 GET $*
    ;;
esac
