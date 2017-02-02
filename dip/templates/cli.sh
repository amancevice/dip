#!/bin/bash

set -e
cd {home}
docker-compose run --rm {name} $*
