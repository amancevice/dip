"""
dip CLI tool main entrypoint
"""
import json
import os

import click
from . import cli
from . import config
from . import exc
from . import options


@click.group()
def dip():
    """ Install CLIs using docker-compose.

        See https://github.com/amancevice/dip for details & instructions.
    """
    pass  # pragma: no cover


@click.command(name='help')
@click.pass_context
def help_(ctx):
    """ Show this message. """
    click.echo(ctx.parent.command.get_help(ctx.parent))


@click.command(name='home')
@options.NAME
def home_(name):
    """ Display home dir of installed CLI. """
    with config.config_for(name) as cfg:
        click.echo(cfg['home'])


@click.command()
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


@click.group('config', chain=True, invoke_without_command=True)
@click.pass_context
def config_(ctx):
    """ Show current dip configuration. """
    # Echo config if no subcommand
    if ctx.invoked_subcommand is None:
        with config.current() as cfg:
            click.echo(json.dumps(cfg, sort_keys=True, indent=4))


@click.command(name='path')
@options.PATH
def path_(path):
    """ Set default PATH. """
    # Update config
    config.set_path(path)

    # Finish
    click.echo("Default path set to '{path}'".format(path=path))


@click.command()
@options.NAME
@options.HOME
@options.PATH_OPT
@options.DRY_RUN
def install(name, home, path, dry_run):
    """ Install CLI by name.

        \b
        dip install fizz               # Default is current dir
        dip install fizz .             # Explicit path
        dip install fizz /path/to/dir  # Absolute path
    """
    # Write executable
    if dry_run is False:
        cli.write(name, os.path.abspath(home), path)

    # Update config
    config.install(name, home, path)

    # Finish
    click.echo("Installed '{name}' to {path}".format(name=name, path=path))


@click.command()
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
                     ['docker-compose', 'pull']+service)
        except (OSError, IOError):
            raise exc.DipError("Unable to pull updates for '{name}'"
                               .format(name=name))


@click.command()
@options.NAME
def uninstall(name):
    """ Uninstall CLI by name. """
    with config.config_for(name) as cfg:
        # Remove executable
        cli.remove(name, cfg['path'])

        # Update config
        config.uninstall(name)

        # Finish
        click.echo("Uninstalled '{name}'".format(name=name))


dip.add_command(config_)
dip.add_command(help_)
dip.add_command(install)
dip.add_command(home_)
dip.add_command(pull)
dip.add_command(show)
dip.add_command(uninstall)
config_.add_command(help_)
config_.add_command(path_)
