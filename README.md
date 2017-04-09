# dip

[![build](https://travis-ci.org/amancevice/dip.svg?branch=master)](https://travis-ci.org/amancevice/dip)
[![codecov](https://codecov.io/gh/amancevice/dip/branch/master/graph/badge.svg)](https://codecov.io/gh/amancevice/dip)
[![pypi](https://badge.fury.io/py/dip.svg)](https://badge.fury.io/py/dip)


Install CLIs using docker-compose.

## Installation

```bash
pip install dip
```

Installed CLIs also depend on the `realpath` command, which can be installed on macOS with

```bash
brew install coreutils
```

## Simple Usage

1. Write a CLI in whatever language you choose
2. Create a `Dockerfile` that installs your CLI application
3. Write a `docker-compose.yml` file that builds the image and defines the run-time configuration
4. Run `dip install <service>` to install the service as an executable command
5. Run `dip uninstall <service>` to remove the executable from the file system

## Tracking a git remote

1. Follow steps 1-3 above
2. Commit these files to a branch on a git remote (eg. `origin/master`)
3. Run `dip install <service> --remote <remote>/<branch>` to install the service as an executable command that will track changes to `docker-compose.yml` on the supplied remote/branch
4. Run `dip uninstall <service>` to remove the executable from the file system

If a CLI is installed with the `--remote` flag, any differences between the local and remote `docker-compose.yml` files will trigger a diff message and the CLI will sleep for 10s.

## Installing with ENV variables

Use the `--env` option to install the CLI with an environment variable set. Use the `--secret` option to enter the environment variable in an interactive prompt where the input is hidden.

Ex.

```bash
cd /path/to/docker-compose-dir
dip install mycli . \
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
version: '2'
services:
  dipex:
    image: amancevice/dipex
    build: .
    environment:
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
    volumes:
      - ~/.aws:/root/.aws
```

### Installing the CLI

Installing the CLI is as simple as:

```bash
dip install dipex
```

Or, if you would like to install tracking a remote:

```bash
dip install dipex --remote origin/master
```

If you are not currently inside the directory where your `docker-compose.yml` file is, you may supply it as a positional argument:

```bash
dip install dipex /path/to/docker-compose-dir [--remote origin/master]
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
    "path": "/usr/local/bin",
    "home": "/path/to/dip/config.json",
    "version": "0.2.3",
    "dips": {},
}
```

The default `PATH` for installations can be changed:

```bash
$ dip config --global path
/usr/local/bin
```

```bash
$ dip config --global path --set /path/to/bin
$ dip config --global path
/path/to/bin
```

After an item is installed it will appear in the `dips` key:

```bash
$ dip install dipex /path/to/docker-compose-dir
$ dip config
{
    "path": "/path/to/bin",
    "home": "/path/to/dip/config.json",
    "version": "0.2.3",
    "dips": {
        "dipex": {
            "home": "/path/to/docker-compose-dir",
            "path": "/path/to/bin",
            "remote": null,
            "branch": null,
            "env": {}
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
    "home": "/path/to/dip/config.json",
    "version": "0.2.3",
    "dips": {
        "dipex": {
            "home": "/path/to/docker-compose-dir",
            "path": "/my/bin",
            "remote": null,
            "branch": null,
            "env": {}
        }
    }
}
```

Use `dip config NAME` to display the configuration of an installed CLI:

```bash
$ dip config dipex
{
    "home": "/path/to/docker-compose-dir",
    "path": "/my/bin",
    "remote": null,
    "branch": null,
    "env": {}
}
```

Use `dip config NAME KEY` to display a given configuration item

```bash
$ dip config dipex home
/path/to/docker-compose-dir

# Handy trick...
$ cd $(dip config dipex home)
```

Use `dip show NAME` to print the contents of the `docker-compose.yml` to screen:

```bash
$ dip show dipex
version: '2'
services:
  dipex:
    # ...
```
