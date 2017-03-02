"""
dip CLI tool main entrypoint
"""
import json
import functools
import os
import sys
from copy import deepcopy

import click
import colored
from . import cli
from . import config
from . import exc
from . import options


# pylint: disable=unused-argument
@click.group()
@options.VERSION
def dip(version):
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


@dip.command('config')
@options.GLOBAL
@options.SET
@options.KEYS
def config_(keys, **kwargs):
    """ Show current dip configuration. """
    gbl = kwargs['global']
    s_t = kwargs['set']
    with config.current() as cfg:
        if gbl is not True and any(keys):
            keys = (u'dips',) + keys
        if s_t is not None:
            upd = functools.reduce(lambda x, y: {y: x}, reversed(keys), s_t)
            new_cfg = dict_merge(cfg, upd)
            config.write(new_cfg)
        else:
            for key in keys:
                try:
                    cfg = cfg[key]
                except KeyError:
                    sys.exit(1)
            if isinstance(cfg, dict):
                click.echo(json.dumps(cfg, sort_keys=True, indent=4))
            else:
                click.echo(cfg)


@dip.command()
@options.NAME
@options.HOME
@options.PATH_OPT
@options.DRY_RUN
@options.REMOTE
def install(name, home, path, dry_run, remote):
    """ Install CLI by name.

        \b
        dip install fizz               # Default is current dir
        dip install fizz .             # Explicit path
        dip install fizz /path/to/dir  # Absolute path
    """
    # Write executable
    if dry_run is False:
        cli.write(name, path)

    # Update config
    config.install(name, home, path, remote)

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


def dict_merge(target, *args):
    """ Taken from: http://blog.impressiver.com/post/31434674390 """
    # Merge multiple dicts
    if len(args) > 1:
        for obj in args:
            dict_merge(target, obj)
        return target

    # Recursively merge dicts and set non-dict values
    obj = args[0]
    if not isinstance(obj, dict):
        return obj
    for key, val in obj.items():
        if key in target and isinstance(target[key], dict):
            dict_merge(target[key], val)
        else:
            target[key] = deepcopy(val)
    return target
