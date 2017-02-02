"""
dip CLI tool main entrypoint
"""
import json
import os
import sys

import click
from . import cli
from . import config as dipconfig

CONFIG = dipconfig.read()


@click.group()
def dip():
    """ Install CLIs using docker-compose.

        See https://github.com/amancevice/dip for details & instructions.
    """
    pass  # pragma: no cover


@click.group()
def config():
    """ Show/set/reset dip config. """
    pass  # pragma: no cover


@click.command()
def show():
    """ Show dip config JSON. """
    click.echo(json.dumps(CONFIG, sort_keys=True, indent=4))


@click.command(name='set')
@click.argument('name')
@click.argument('value')
def setcmd(name, value):
    """ Set config value. """
    CONFIG[name] = value
    dipconfig.write_config(CONFIG)
    click.echo(json.dumps(CONFIG, sort_keys=True, indent=4))


@click.command()
def reset():
    """ Reset config to defaults. """
    globals()['CONFIG'] = dipconfig.reset()
    click.echo(json.dumps(CONFIG, sort_keys=True, indent=4))


@click.command()
@click.argument('name')
@click.argument('home', default='.')
@click.option('--path', default=CONFIG['path'],
              help="Path to write executable [default: {}]"
              .format(CONFIG['path']))
@click.option('--dry-run/--no-dry-run', default=False,
              help='Do not write executable')
def install(name, home, path, dry_run):
    """ Install CLI using PATH to docker-compose.yml

        \b
        dip install fizz               # Default is current dir
        dip install fizz .             # Explicit path
        dip install fizz /path/to/dir  # Absolute path
    """
    # Get abspath for home
    home = os.path.abspath(home)

    # Get path to write executable
    exe = os.path.join(path, name)

    # Write executable
    if dry_run is False:
        cli.write_cli(exe, name, home)

    # Update config
    CONFIG['dips'][name] = home
    dipconfig.write_config(CONFIG)

    # Finish
    click.echo("Installed {name} to {exe}".format(name=name, exe=exe))


@click.command()
@click.argument('name')
@click.option('--path', default='/usr/local/bin',
              help="Path to write executable [default: {}]"
              .format(CONFIG['path']))
def uninstall(name, path):
    """ Uninstall CLI by name. """
    # Get path to delete executable
    exe = os.path.join(path, name)

    # Remove executable
    try:
        cli.remove_cli(exe)
    except OSError:
        click.echo("'{name}' is not installed.".format(name=name))
        sys.exit(1)

    # Update config
    try:
        del CONFIG['dips'][name]
        dipconfig.write_config(CONFIG)
    except KeyError:
        pass

    # Finish
    click.echo("Uninstalled {name} from {exe}".format(name=name, exe=exe))


dip.add_command(config)
dip.add_command(install)
dip.add_command(uninstall)
config.add_command(show)
config.add_command(setcmd)
config.add_command(reset)
