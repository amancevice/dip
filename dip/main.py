"""
dip CLI tool main entrypoint
"""
import json
import subprocess

import click
import docker
from dip import __version__
from dip import colors
from dip import errors
from dip import options
from dip import settings
from dip import utils


def clickerr(func):
    """ Decorator to catch errors and re-raise as ClickException. """
    # pylint: disable=missing-docstring
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except errors.DipError as err:
            raise click.ClickException(str(err))
    wrapper.__doc__ = func.__doc__
    return wrapper


def warnsleep(app):
    """ Warn about app divergence and sleep. """
    # Warn about divergence
    warn = '\n'\
        'Local service has diverged from remote or is inaccessible.\n'\
        'Sleeping for {}s\n'\
        'CTRL-C to exit\n'.format(app.repo.sleeptime)
    click.echo(colors.amber(warn), err=True)

    # Give hint to upgrade
    upgrade = 'dip upgrade {}'.format(app.name)
    hint = 'Run `{}` to git-pull updates from remote\n'\
        .format(colors.teal(upgrade))
    click.echo(hint, err=True)

    # Sleep
    app.repo.sleep()


def warnask(app):
    """ Warn about app divergence and ask to upgrade. """
    # Warn about divergence
    warn = '\nLocal service has diverged from remote or is inaccessible.'
    click.echo(colors.amber(warn), err=True)

    # Ask to upgrade
    upgrade = colors.teal('Attempt to upgrade before continuing?')
    if click.confirm(upgrade):
        # Upgrade
        app.repo.pull()
        click.echo(err=True)
    else:
        override = colors.teal('Continue without upgrading?')
        if not click.confirm(override):
            goodbye = 'Please resolve these changes before re-attempting.\n'
            click.echo(goodbye, err=True)
            raise SystemExit(1)


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-v', '--version')
def dip():
    """ Install CLIs using docker-compose.

        The following ENV variables are supported by `dip`:

        \b
        :DIP_HOME: The location of the dip settings.json file
        :DIP_PATH: The default location of installed executables

        See https://github.com/amancevice/dip for more information.
    """
    pass  # pragma: no cover


@dip.command('config')
@options.EDIT
@options.KEYS
@clickerr
def dip_config(edit, keys):
    """ Show current dip configuration.

        \b
        dip config NAME             # Get NAME config dict
        dip config NAME git remote  # Get name of remote
    """
    with settings.load() as cfg:
        if edit:
            try:
                subprocess.call([utils.editor(), cfg.filepath])
            except KeyError:
                raise click.ClickException('EDITOR value not defined in ENV')
        else:
            working = cfg.data
            for key in keys:
                try:
                    working = working[key]
                except (KeyError, TypeError):
                    raise SystemExit(1)

            if isinstance(working, dict):
                click.echo(json.dumps(working, indent=4, sort_keys=True))
            else:
                click.echo(working)


@dip.command('install')
@options.NAME
@options.HOME
@options.PATH
@options.REMOTE
@options.ENV
@options.SECRET
@options.SLEEP
@options.NO_EXE
@clickerr
def dip_install(name, home, path, remote, env, secret, sleep, no_exe):
    """ Install CLI by name.

        \b
        dip install fizz .                   # Relative path
        dip install fizz /path/to/dir        # Absolute path
        dip install fizz . -r origin/master  # Tracking git remote/branch
    """
    # pylint: disable=too-many-arguments
    with settings.saveonexit() as cfg:
        # Interactively set ENV
        for sec in secret:
            env[sec] = click.prompt(sec, hide_input=True)  # pragma: no cover

        # Parse git config
        remote, branch = remote
        git = {'remote': remote, 'branch': branch, 'sleep': sleep}

        # Install
        if no_exe:
            app = cfg[name] = settings.Dip(name, home, path, env, git)
        else:
            app = cfg.install(name, home, path, env, git)

        # Validate configuration
        app.validate()

        # Finish
        click.echo("Installed {name} to {path}".format(
            name=colors.teal(app.name),
            path=colors.blue(app.path)))


@dip.command('list')
@clickerr
def dip_list():
    """ List installed CLIs. """
    with settings.load() as cfg:
        if any(cfg):
            click.echo()
            homes = [utils.contractuser(cfg[x].home) for x in cfg]
            maxname = max(len(x) for x in cfg)
            maxhome = max(len(x) for x in homes)
            for key in sorted(cfg):
                app = cfg[key]
                name = colors.teal(app.name.ljust(maxname))
                home = colors.blue(utils.contractuser(app.home).ljust(maxhome))
                remote = branch = None
                tpl = "{name} {home}"
                if app.repo:
                    try:
                        remote = app.repo.remotename
                        branch = app.repo.branch
                        tpl += " {remote}/{branch}"
                    except Exception:  # pylint:  disable=broad-except
                        tpl += colors.red(' [git error]')
                click.echo(tpl.format(name=name,
                                      home=home,
                                      remote=remote,
                                      branch=branch))
            click.echo()


@dip.command('pull')
@options.NAME
@clickerr
def dip_pull(name):
    """ Pull updates from docker-compose. """
    with settings.diffapp(name) as app_diff:
        app, diff = app_diff
        if diff and app.git.get('sleep'):
            warnsleep(app)
        elif diff:
            warnask(app)
        try:
            return app.service.pull()
        except docker.errors.APIError:
            err = "Could not pull '{}' image".format(name)
            click.echo(colors.red(err), err=True)
        raise SystemExit(1)


@dip.command('reset')
@options.FORCE
@clickerr
def dip_reset(force):
    """ Reset dip configuration to defaults. """
    if force:
        settings.reset()


@dip.command('run')
@options.NAME
@options.ARGS
@clickerr
def dip_run(name, args):
    """ Run dip CLI. """
    with settings.diffapp(name) as app_diff:
        app, diff = app_diff
        if diff and app.git.get('sleep'):
            warnsleep(app)
        elif diff:
            warnask(app)
        app.run(*args)


@dip.command('show')
@options.NAME
@clickerr
def dip_show(name):
    """ Show service configuration. """
    with settings.diffapp(name) as app_diff:
        app, diff = app_diff
        if diff and app.git.get('sleep'):
            warnsleep(app)
        elif diff:
            warnask(app)
        for definition in app.definitions:
            click.echo("\n{}\n".format(definition.strip()))


@dip.command('uninstall')
@options.NAMES
@clickerr
def dip_uninstall(names):
    """ Uninstall CLI by name. """
    for name in names:
        with settings.saveonexit() as cfg:
            try:
                cfg.uninstall(name)
                click.echo("Uninstalled {name}".format(name=colors.red(name)))
            except KeyError:
                pass


@dip.command('upgrade')
@options.NAMES
@clickerr
def dip_upgrade(names):
    """ Upgrade CLI by pulling from git remote. """
    for name in names:
        with settings.getapp(name) as app:
            try:
                app.repo.pull()
            except AttributeError:
                pass
