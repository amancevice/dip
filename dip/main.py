"""
dip CLI tool main entrypoint
"""
import os

import click
from . import cli
from . import config

CONFIG = config.read()


@click.group()
def dip():
    """ Entrypoint. """
    pass


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
    cli.remove_cli(exe)

    # Finish
    click.echo("Uninstalled {name} from {exe}".format(name=name, exe=exe))


dip.add_command(install)
dip.add_command(uninstall)
