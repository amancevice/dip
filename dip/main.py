"""
dip CLI tool main entrypoint
"""
import json
import os
import sys

import click
import colored
from . import cli
from . import config
from . import exc
from . import options


# pylint: disable=unused-argument
@click.group()
@options.VERSION
def dip():
    """ Install CLIs using docker-compose.

        See https://github.com/amancevice/dip for details & instructions.
    """
    pass  # pragma: no cover


@dip.command(name='help')
@click.pass_context
def help_(ctx):
    """ Show this message. """
    click.echo(ctx.parent.command.get_help(ctx.parent))


@dip.command()
@options.NAME
def show(name):
    """ Show contents of docker-compose.yml. """
    with config.config_for(name) as cfg:
        # Get path to docker-compose.yml
        path = os.path.join(cfg['home'], 'docker-compose.yml')

        # Echo contents of docker-compose.yml
        try:
            with open(path, 'r') as compose:
                click.echo(compose.read())
        except (OSError, IOError):
            raise exc.DockerComposeError(name)


# pylint: disable=invalid-name
@dip.command('config')
@options.GLOBAL
@options.REMOVE
@options.SET
@options.OPTIONAL_NAME
@options.KEYS
def config_(gbl, rm, s_t, name, keys):
    """ Show current dip configuration.

        \b
        dip config NAME                      # Get NAME config dict
        dip config NAME remote               # Get name of NAME remote
        dip config NAME remote --set origin  # Set NAME remote to 'origin'
        dip config NAME --rm remote          # Remove NAME remote key
        dip config --global home              # Get path to global config file
    """
    with config.current() as cfg:

        # Set up keys for --global or normal
        if gbl:
            keys = (gbl,)
        elif name:
            keys = ('dips', name) + keys

        # Set a config value if --set is provided
        if s_t is not None:
            config.set_config(cfg, keys, s_t)

        # Remove a config value
        elif rm is not None:
            config.rm_config(cfg, keys, rm)

        # Otherwise, drill into config to fetch requested config
        else:
            # Get value or exit
            try:
                val = config.get_config(cfg, keys)
            except KeyError:
                sys.exit(1)

            # Print pretty JSON if result is a dict
            if isinstance(val, dict):
                click.echo(json.dumps(val, sort_keys=True, indent=4))
            # If it's valid echo result
            elif val:
                click.echo(val)
            # Otherwise, exit
            else:
                sys.exit(1)


@dip.command('env')
@options.NAME
def env_(name):
    """ Show docker-compose ENV flags. """
    with config.current() as cfg:
        try:
            env = cfg['dips'][name]['env']
            if env:
                cmd = ['='.join(x) for x in env.items()]
                click.echo('-e ' + ' -e '.join(cmd))
        except KeyError:
            sys.exit(1)


# pylint: disable=too-many-arguments
@dip.command()
@options.NAME
@options.HOME
@options.PATH_OPT
@options.REMOTE
@options.ENV
@options.SECRET
def install(name, home, path, remote, env, secret):
    """ Install CLI by name.

        \b
        dip install fizz               # Default is current dir
        dip install fizz .             # Explicit path
        dip install fizz /path/to/dir  # Absolute path
    """
    # Interactively set ENV
    for sec in secret:
        env[sec] = click.prompt(sec, hide_input=True)  # pragma: no cover

    # Write executable
    cli.write(name, path)

    # Update config
    config.install(name, home, path, remote, env)

    # Finish
    msg = "Installed {name} to {path}"
    cname = colored.stylize(name, colored.fg('spring_green_1'))
    cpath = colored.stylize(path, colored.fg('blue'))
    click.echo(msg.format(name=cname, path=cpath))


@dip.command()
@options.NAME
@options.SERVICE
def pull(name, service):
    """ Pull updates from docker-compose. """
    # Get services to pull
    service = service or (name,)
    service = list(service)

    # Get CLI config
    with config.config_for(name) as cfg:
        try:
            os.chdir(cfg['home'])
            os.execv('/usr/local/bin/docker-compose',
                     ['docker-compose', 'pull'] + service)
        except (OSError, IOError):
            raise exc.DipError("Unable to pull updates for '{name}'"
                               .format(name=name))


@dip.command()
@options.NAME
def uninstall(name):
    """ Uninstall CLI by name. """
    with config.config_for(name) as cfg:
        # Remove executable
        cli.remove(name, cfg['path'])

        # Update config
        config.uninstall(name)

        # Finish
        cname = colored.stylize(name, colored.fg('red'))
        click.echo("Uninstalled {name}".format(name=cname))
