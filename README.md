# dip

[![build](https://travis-ci.org/amancevice/dip.svg?branch=master)](https://travis-ci.org/amancevice/dip)
[![codecov](https://codecov.io/gh/amancevice/dip/branch/master/graph/badge.svg)](https://codecov.io/gh/amancevice/dip)
[![pypi](https://badge.fury.io/py/dip.svg)](https://badge.fury.io/py/dip)


Install CLIs using docker-compose.

## Installation

```bash
pip install dip
```

## Simple Usage

1. Write a CLI in whatever language you choose
2. Create a `Dockerfile` that installs your CLI application
3. Write a `docker-compose.yml` file that builds the image and defines the run-time configuration
4. Run `dip install <service>` to install the service as an executable command
5. Run `dip uninstall <service>` to remove the executable from the file system

### Why Docker?

When building a custom application it is sometimes necessary to include libraries and packages.

If these dependencies become too burdensome, you may consider using Docker to avoid problems handing this application off from user to user.

The `docker-compose` tool adds additional functionality wherein you can define specific run-time configurations.

### What does `dip` do?

Installing a CLI using `dip install` is essentially syntactic sugar for:

```bash
cd /path/to/docker-compose-dir
docker-compose run --rm <svc> $*
```

You can accomplish the same thing with aliases, but this is a little more fun.

## Example

Consider the task of writing a *very* simple CLI to pull data out of Redis and write it to S3.

In order to do this we will use Python, the AWS CLI and the Redis CLI libraries.

### Writing a CLI

Our CLI will be intentionally very simple; it will accept a single positional argument.

If this argument is the string `setup` it will seed Redis with some dummy data.
Otherwise, it will query Redis for this key, and write the result to a text file on S3.

```bash
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
    redis-cli -h $REDIS_HOST -n 1 GET $* > /tmp/result
    echo "Pushing result to $S3_PREFIX/result..."
    aws s3 cp /tmp/result $S3_PREFIX/result
    ;;
esac
```

### Writing a `Dockerfile`

In our `Dockerfile` we should install all our software, copying in our CLI above, and define a volume for mounting our AWS credentials:

```Dockerfile
FROM python:3.6-alpine
RUN pip install awscli && apk add --no-cache redis
COPY cli.sh /root/cli.sh
VOLUME /root/.aws
ENTRYPOINT ["/bin/sh", "cli.sh"]
```

### Writing a `docker-compose.yml`

Our `docker-compose.yml` will define our service, `dipex`, and lay down configurations for a Redis host, an S3 prefix (where our file will go), and mount in our `~/.aws` directory:

```
version: '2'
services:
  dipex:
    image: dipex
    build: .
    environment:
      S3_PREFIX: s3://mybucket/path/to/my/prefix
      REDIS_HOST: my-redis-host.com
    volumes:
      - "~/.aws:/root/.aws"
```

### Installing the CLI

Installing the CLI is as simple as:

```bash
dip install dipex
```

If you are not currently inside the directory where your `docker-compose.yml` file is, you may supply it as a positional argument:

```bash
dip install dipex /path/to/docker-compose-dir
```

### Using the CLI

```bash
$ dipex setup
Pushing data to redis...
1) "mykey1"
2) "mykey0"
3) "mykey2"

$ dipex mykey1
Feching mykey1 from my-redis-host.com...
Pushing result to s3://bucket/path/to/my/prefix/result...
```

### Uninstall the CLI

Uninstalling the CLI simply removes the executable and can be done using the `uninstall` subcommand:

```bash
dip uninstall dipex
```

# Extended Configuration

The default configuration can be viewed using the `dip config` command:

```json
{
    "path": "/usr/local/bin",
    "dips": {}
}
```

The default `PATH` for installations can be changed:

```bash
$ dip config path /path/to/bin
{
    "path": "/path/to/bin",
    "dips": {}
}
```

After an item is installed it will appear in the `dips` key:

```bash
$ dip install dipex /path/to/docker-compose-dir
$ dip config
{
    "path": "/path/to/bin",
    "dips": {
        "dipex": {
            "home": "/path/to/docker-compose-dir",
            "path": "/path/to/bin"
        }
    }
}
```

Use the `--path` option when installing/uninstalling to override the default path & use a custom one:

```bash
$ dip install --path /my/bin dipex /path/to/docker-compose-dir
$ dip config
{
    "path": "/path/to/bin",
    "dips": {
        "dipex": {
            "home": "/path/to/docker-compose-dir",
            "path": "/my/bin"
        }
    }
}
```

Use `dip home NAME` to find the home directory of the installed CLI:

```bash
$ dip home dipex
/path/to/docker-compose-dir

# Handy trick...
$ cd $(dip home dipex)
```

Use `dip show NAME` to print the contents of the `docker-compose.yml` to screen:

```bash
$ dip show dipex
version: '2'
services:
  dipex:
    # ...
```
