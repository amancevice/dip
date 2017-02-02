# dip

[![build](https://travis-ci.org/amancevice/dip.svg?branch=master)](https://travis-ci.org/amancevice/dip)
[![codecov](https://codecov.io/gh/amancevice/dip/branch/master/graph/badge.svg)](https://codecov.io/gh/amancevice/dip)
[![pypi](https://badge.fury.io/py/dip.svg)](https://badge.fury.io/py/dip)
[![python](https://img.shields.io/badge/python-2.7--3.6-blue.svg)](https://img.shields.io/badge/python-2.7--3.6-blue.svg)


Install CLIs using docker-compose

## Installation

```bash
pip install dip
```

## Configuration

The default configuration can be viewed using the `dip config show` command:

```json
{
    "path": "/usr/local/bin",
    "dips": {}
}
```

The default `PATH` for installations can be changed:

```bash
$ dip config set path /path/to/bin
{
    "path": "/path/to/bin",
    "dips": {}
}
```

After an item is installed it will appear in the `dips` key:

```bash
$ dip install dipex /path/to/docker-compose-dir
$ dip config show
{
    "path": "/path/to/bin",
    "dips": {
        "dipex": "/path/to/bin/dipex"
    }
}
```

Alternatively, use the `--path` option when installing/uninstalling to use a custom path for a given item.

```bash
$ dip install --path /my/bin dipex /path/to/docker-compose-dir
$ dip config show
{
    "path": "/path/to/bin",
    "dips": {
        "dipex": "/my/bin/dipex"
    }
}
```


## Usage

Use `dip` to install a CLI using a `docker-compose.yml` file.

Your `docker-compose.yml` file should define at least one service using the name of the CLI you wish to define.

For example, if you wished to create a CLI named `fizz` you might create the following `docker-compose.yml`:

```
version: '2'
services:
  fizz:
    image: fizz
    build: .
```

Install the CLI using the `dip install` command, supplying the name of the service and the path to the `docker-compose.yml` file (defaults to the current directory):

```bash
dip install fizz /path/to/docker-compose-dir
```

## Example

In this example we will walk through creating a very simple wrapper around the `redis-cli` tool.


### Create a CLI

First, we will create a *very* simple bash script -- [`cli.sh`](./example/cli.sh) -- that will control our CLI. This script will accept a keyword `setup` that will seed our redis backend with some dummy data. If the argument to the CLI is not `setup`, we will assume that the user is attempting to get a key with the same name as the argument:

```bash
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
```

### Wrap the CLI in a Docker image

Next, we will create a [`Dockerfile`](./example/Dockerfile) that is capable of communicating with a redis service. We will start with the `alpine` image, install the redis-cli and copy our CLI script into the image & make it our entrypoint:

```Dockerfile
FROM alpine
RUN apk add --no-cache redis
COPY cli.sh .
ENTRYPOINT ["/bin/sh", "/cli.sh"]
```

### Use `docker-compose` to define the CLI as a service

Finally, we will create a [`docker-compose.yml`](./example/docker-compose.yml) file that will define our redis backend and the `dipex` CLI:

```
version: '2'
services:
  redis:
    image: redis:alpine
  dipex:
    image: dipex
    build: .
    depends_on:
      - redis
```

Notice that our `dipex` service depends on the redis service. This will force the redis service to start before `dipex` can execute (with some caveats).

### Install the CLI

Now we are ready to install the CLI:

```bash
$ dip install dipex ./example
Installed dipex to /usr/local/bin/dipex

$ dipex setup
Pushing data to redis...
1) "mykey1"
2) "mykey0"
3) "mykey2"

$ dipex mykey1
"myval1"

$ dipex fizz
(nil)
```

### Uninstall the CLI

Uninstalling the CLI simply removes the executable and can be done using the `uninstall` subcommand:

```bash
dip uninstall dipex
```
