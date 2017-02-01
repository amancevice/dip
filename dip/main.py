"""
dip CLI tool main entrypoint
"""
import os

import click
# from compose.cli import main as docker_compose
from . import templates


@click.group()
def dip():
    """ Entrypoint. """
    pass


@click.command()
@click.argument('name')
@click.argument('path', default='.')
@click.option('--exe', default='/usr/local/bin',
              help='Path to write executable')
@click.option('--dry-run/--no-dry-run', default=False,
              help='Do not write executable')
def install(name, path, exe, dry_run):
    """ Install CLI. """
    # Move to install directory
    os.chdir(path)
    pwd = os.getcwd()

    # Get path to write executable
    path = os.path.join(exe, name)

    # Get body of executable
    bash = templates.bash(name, pwd)

    # Write executable
    if dry_run is False:
        with open(path, 'w') as executable:
            executable.write(bash)
        os.chmod(path, 0o755)

    # Dry run
    else:
        click.echo(bash)

    # Finish
    click.echo("Installed {name} to {path}".format(name=name, path=path))


@click.command()
@click.argument('name')
@click.option('--exe', default='/usr/local/bin',
              help='Path to write executable')
def uninstall(name, exe):
    """ Uninstall CLI. """
    # Get path to delete executable
    path = os.path.join(exe, name)

    # Remove file
    os.remove(path)

    # Finish
    click.echo("Uninstalled {name} from {path}".format(name=name, path=path))


dip.add_command(install)
dip.add_command(uninstall)
