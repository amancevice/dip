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
4. Run `dip install <service> .` to install the service as an executable command
5. Run `dip uninstall <service> .` to remove the executable from the file system

```bash
mkdir example
cd example
touch docker-compose.yml
# Edit docker-compose.yml to include 'dipex' service...
dip install dipex .
```

## Tracking a git remote

1. Follow steps 1-3 above
2. Commit these files to a branch on a git remote (eg. `origin/master`)
3. Run `dip install <service> . --remote <remote>/<branch>` to install the service as an executable command that will track changes to `docker-compose.yml` on the supplied remote/branch
4. Run `dip uninstall <service>` to remove the executable from the file system

```bash
git clone git@github.com:owner/repo-with-docker-compose.git
cd repo-with-docker-compose
dip install dipex . --remote origin/master
```

If a CLI is installed with the `--remote` flag, any differences between the local and remote `docker-compose.yml` files will trigger a prompt asking if the user wishes to upgrade (git pull).

If the user declines to upgrade he/she must resolve the conflict before continuing.

Alternatively, use the `--sleep` option to show the user the diff, then sleep for the provided time (in seconds) instead of waiting on user input.

```bash
dip install dipex . --remote origin/master --sleep 10
```

## Upgrading from a git remote

1. Follow the steps above to install your CLI with a remote
2. If the remote moves ahead of the local, you will see a warning when executing CLI commands
3. use `dip upgrade <service>` to pull changes from the remote

## Installing with ENV variables

Use the `--env` option to install the CLI with an environment variable set. Use the `--secret` option to enter the environment variable in an interactive prompt where the input is hidden.

Ex.

```bash
dip install mycli /path/to/project \
  --remote origin/master \
  --env FIZZ=BUZZ
```

Will generate an executable with the name `mycli`, monitor the `origin/master` remote/branch for changes and set the `ENV` variable `FIZZ` to the value `BUZZ` each time the `mycli` is executed.

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

Consider a trivial example of a Docker image with the AWS CLI installed.

### Writing a `Dockerfile`

We will create a [`Dockerfile`](./example/Dockerfile) that installs this CLI and configures a `VOLUME` for mounting your AWS credentials:

```Dockerfile
FROM alpine
RUN apk add --no-cache less groff python3 && \
    pip3 install awscli
VOLUME /root/.aws
ENTRYPOINT ["aws"]
```

### Writing a `docker-compose.yml`

Our `docker-compose.yml` will define our service, `dipex`, and configure our AWS credentials (either through `ENV` variables or the `~/.aws` directory):

```
version: '3'
services:
  dipex:
    image: amancevice/dipex
    build: .
    environment:
      AWS_ACCESS_KEY_ID:
      AWS_SECRET_ACCESS_KEY:
    volumes:
      - ~/.aws:/root/.aws
```

### Installing the CLI

Installing the CLI is as simple as:

```bash
dip install dipex .
```

Or, if you would like to install tracking a remote:

```bash
dip install dipex . --remote origin/master
```

If you are not currently inside the directory where your `docker-compose.yml` file is, supply it as a positional argument:

```bash
dip install dipex /path/to/project [--remote origin/master]
```

### Using the CLI

```bash
$ dipex s3 ls s3://bkt/path/to/key
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
    "dipex": {
        "git": {
            "branch": "master",
            "remote": "origin"
        },
        "home": "/path/to/project",
        "name": "dipex",
        "path": "/usr/local/bin"
    },
}
```

The default `PATH` for installations can be changed by setting `ENV` variables:

```bash
export DIP_HOME=/path/to/settings.json
export DIP_PATH=/bath/to/bin
```

After an item is installed it will appear in the `dips` key:

```bash
$ dip install dipex /path/to/project
$ dip config
{
    "dipex": {
        "home": "/path/to/project",
        "name": "dipex",
        "path": "/usr/local/bin"
    }
}
```

Use the `--path` option when installing/uninstalling to override the default path & use a custom one:

```bash
$ dip install --path /my/bin dipex /path/to/project
$ dip config
{
    "dipex": {
        "home": "/path/to/project",
        "name": "dipex",
        "path": "/my/bin"
    }
}
```

Use `dip config NAME` to display the configuration of an installed CLI:

```bash
$ dip config dipex
{
    "home": "/path/to/project",
    "name": "dipex",
    "path": "/my/bin"
}
```

Use `dip config NAME KEY` to display a given configuration item

```bash
$ dip config dipex home
/path/to/project

# Handy trick...
$ cd $(dip config dipex home)
```

Use `dip show NAME` to print the contents of the `docker-compose.yml` to screen:

```bash
$ dip show dipex
version: '3'
services:
  dipex:
    # ...
```
