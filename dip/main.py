"""
dip CLI tool main entrypoint
"""
import json
import sys

import click
from . import __version__
from . import contexts
from . import colors
from . import config
from . import errors
from . import options
from . import utils


@click.group(context_settings={'obj': config.load()})
@click.version_option(__version__)
@click.pass_context
def dip(ctx):
    """ Install CLIs using docker-compose.

        See https://github.com/amancevice/dip for details & instructions.
    """
    pass  # pragma: no cover


@dip.command('config')
@options.GLOBAL
@options.KEYS
@click.pass_context
def dip_config(ctx, gbl, keys):
    """ Show current dip configuration.

        \b
        dip config NAME                      # Get NAME config dict
        dip config NAME remote               # Get name of NAME remote
        dip config --global home             # Get path to global config file
    """
    # Set up keys for --global or normal
    if not gbl and any(keys):
        keys = ('dips',) + keys

    working = ctx.obj.config
    for key in keys:
        try:
            working = working[key]
        except (KeyError, TypeError):
            sys.exit(1)

    if isinstance(working, dict):
        click.echo(json.dumps(working, indent=4, sort_keys=True))
    else:
        click.echo(working)


# pylint: disable=too-many-arguments
@dip.command('install')
@options.NAME
@options.HOME
@options.PATH
@options.REMOTE
@options.ENV
@options.SECRET
@click.pass_context
def dip_install(ctx, name, home, path, remote, env, secret):
    """ Install CLI by name.

        \b
        dip install fizz .                   # Relative path
        dip install fizz /path/to/dir        # Absolute path
        dip install fizz . -r origin/master  # Tracking git remote/branch
    """
    # Interactively set ENV
    for sec in secret:
        env[sec] = click.prompt(sec, hide_input=True)  # pragma: no cover

    # Install
    path = path or ctx.obj.path
    with contexts.preload(ctx, name, home, path) as dip:
        dip.install(name, home, path, env, remote)

    # Finish
    msg = "Installed {name} to {path}"
    click.echo(msg.format(name=colors.teal(name), path=colors.blue(path)))


@dip.command('list')
@click.pass_context
def dip_list(ctx):
    """ List installed CLIs. """
    if any(ctx.obj):
        with utils.newlines(any(ctx.obj)):
            max_name = max(len(x) for x in ctx.obj)
            max_home = max(len(ctx.obj[x].home) for x in ctx.obj)
            for key in sorted(ctx.obj):
                dip = ctx.obj[key]
                name = colors.teal(dip.name.ljust(max_name))
                home = colors.blue(dip.home.ljust(max_home))
                remote = dip.remote
                branch = dip.branch
                if remote and branch:
                    tpl = "{name} {home} @ {remote}/{branch}"
                elif remote:
                    tpl = "{name} {home} @ {remote}"
                else:
                    tpl = "{name} {home}"
                click.echo(tpl.format(name=name,
                                      home=home,
                                      remote=remote,
                                      branch=branch))


@dip.command('pull')
@options.NAME
@click.pass_context
def dip_pull(ctx, name):
    """ Pull updates from docker-compose. """
    try:
        with contexts.load(ctx, name) as dip:
            return dip.service.pull()
    except errors.DipError as err:
        click.echo(err, err=True)
    except Exception:
        click.echo("Could not pull '{name}' image".format(name=name), err=True)
    sys.exit(1)


@dip.command('run')
@options.NAME
@options.ARGS
@click.pass_context
def dip_run(ctx, name, args):
    """ Run dip CLI. """
    with contexts.load(ctx, name) as dip:
        dip.run(*args)


@dip.command('show')
@options.NAME
@click.pass_context
def dip_show(ctx, name):
    """ Show service configuration. """
    with contexts.load(ctx, name) as dip:
        with utils.newlines():
            click.echo(dip.definition.strip())


@dip.command('uninstall')
@options.NAMES
@click.pass_context
def dip_uninstall(ctx, names):
    """ Uninstall CLI by name. """
    for name in names:
        with contexts.lazy_load(ctx, name):
            # Uninstall
            ctx.obj.uninstall(name)

            # Finish
            click.echo("Uninstalled {name}".format(name=colors.red(name)))
