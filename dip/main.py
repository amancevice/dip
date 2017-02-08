"""
dip CLI tool main entrypoint
"""
import json
import os

import click
from . import cli
from . import config as dipcfg
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
    cmd = globals()[ctx.parent.command.name]
    click.echo(cmd.get_help(ctx.parent))


@click.command(name='home')
@options.NAME
def home_(name):
    """ Display home dir of installed CLI. """
    try:
        click.echo(dipcfg.read()['dips'][name]['home'])
    except KeyError:
        raise exc.CliNotInstalled(name)


@click.command()
@options.NAME
def show(name):
    """ Show contents of docker-compose.yml. """
    try:
        path = dipcfg.read()['dips'][name]['home']
        path = os.path.join(path, 'docker-compose.yml')
        with open(path, 'r') as compose:
            click.echo(compose.read())
    except KeyError:
        raise exc.CliNotInstalled(name)
    except IOError:
        raise exc.DockerComposeError(name)


@click.group(chain=True, invoke_without_command=True)
@click.pass_context
def config(ctx):
    """ Show/set/reset dip config. """
    if ctx.invoked_subcommand is None:
        click.echo(json.dumps(dipcfg.read(), sort_keys=True, indent=4))


@click.command(name='path')
@options.PATH
def path_(path):
    """ Set default PATH. """
    cfg = dipcfg.read()
    cfg['path'] = path
    dipcfg.write_config(cfg)
    click.echo(json.dumps(cfg, sort_keys=True, indent=4))


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
    # Get abspath for home
    home = os.path.abspath(home)

    # Get path to write executable
    exe = os.path.join(path, name)

    # Write executable
    if dry_run is False:
        cli.write_cli(exe, name, home)

    # Update config
    options.CONFIG['dips'][name] = {'path': path, 'home': home}
    dipcfg.write_config(options.CONFIG)

    # Finish
    click.echo("Installed {name} to {exe}".format(name=name, exe=exe))


@click.command()
@options.NAME
def uninstall(name):
    """ Uninstall CLI by name. """
    # Get CLI config
    cfg = dipcfg.read()['dips']

    # Remove executable
    try:
        exe = cfg[name]['path']
        cli.remove_cli(os.path.join(exe, name))
    except (KeyError, OSError):
        raise exc.CliNotInstalled(name)

    # Update config
    del cfg[name]
    dipcfg.write_config(cfg)

    # Finish
    click.echo("Uninstalled {name} from {exe}".format(name=name, exe=exe))


dip.add_command(config)
dip.add_command(help_)
dip.add_command(install)
dip.add_command(home_)
dip.add_command(show)
dip.add_command(uninstall)
config.add_command(help_)
config.add_command(path_)
