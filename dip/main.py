"""
dip CLI tool main entrypoint
"""
import json
import os
import re
import sys

import click
import colored
from . import colors
from . import config
from . import exc
from . import options
from . import shell
from . import utils

HOME = os.getenv('HOME')


# pylint: disable=unused-argument
@click.group()
@options.VERSION
def dip():
    """ Install CLIs using docker-compose.

        See https://github.com/amancevice/dip for details & instructions.
    """
    pass  # pragma: no cover


# pylint: disable=invalid-name
@dip.command('config')
@options.GLOBAL
@options.REMOVE
@options.CFG_SET
@options.OPTIONAL_NAME
@options.KEYS
def dip_config(gbl, rm, cfg_set, name, keys):
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
        if cfg_set is not None:
            config.set_config(cfg, keys, cfg_set)

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


# pylint: disable=too-many-arguments
@dip.command('install')
@options.NAME
@options.HOME
@options.PATH_OPT
@options.REMOTE
@options.ENV
@options.SECRET
def dip_install(name, home, path, remote, env, secret):
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
    shell.write(name, path)

    # Update config
    config.install(name, home, path, remote, env)

    # Finish
    msg = "Installed {name} to {path}"
    cname = colored.stylize(name, colors.TEAL)
    cpath = colored.stylize(path, colors.BLUE)
    click.echo(msg.format(name=cname, path=cpath))


@dip.command('list')
def dip_list():
    """ List installed CLIs. """
    with config.current() as cfg:
        with utils.newlines(cfg['dips']):
            pad = any(cfg['dips']) and max(len(x) for x in cfg['dips'])
            for name, clicfg in sorted(cfg['dips'].items()):
                name = colored.stylize(name.ljust(pad), colors.TEAL)
                clicfg['home'] = re.sub(r"^{HOME}".format(HOME=HOME),
                                        '~', clicfg['home'])
                if clicfg.get('remote') and clicfg.get('branch'):
                    tpl = "{name} {home} @ {remote}/{branch}"
                elif clicfg.get('remote'):
                    tpl = "{name} {home} @ {remote}"
                else:
                    tpl = "{name} {home}"
                click.echo(tpl.format(name=name, **clicfg))


@dip.command('pull')
@options.ALL_OPT
@options.ALL_OR_NAME
def dip_pull(all_opt, name):
    """ Pull updates from docker-compose. """
    # Get config
    with config.current() as cfg:

        # Get CLIs to pull
        clis = [x for x in cfg['dips'].items() if all_opt or x[0] == name]

        # Pull each CLI
        for cliname, clicfg in clis:
            try:
                with config.compose_service(cliname, clicfg['home']) as svc:
                    svc.pull()
            except exc.DockerComposeServiceError as err:
                click.echo(err, err=True)


@dip.command('reinstall')
@options.ALL_OPT
@options.ALL_OR_NAME
def dip_reinstall(all_opt, name):
    """ Reinstall CLI by name. """
    # Get config
    with config.current() as cfg:

        # Get CLIs to reinstall
        clis = [x for x in cfg['dips'].items() if all_opt or x[0] == name]

        # Reinstall each CLI
        for cliname, clicfg in clis:
            clipath = clicfg['path']

            # Write executable
            shell.write(cliname, clipath)

            # Show installation
            msg = "Reinstalled {name} to {path}"
            cname = colored.stylize(cliname, colors.TEAL)
            cpath = colored.stylize(clipath, colors.BLUE)
            click.echo(msg.format(name=cname, path=cpath))


@dip.command('show')
@options.NAME
def dip_show(name):
    """ Show service configuration. """
    with config.config_for(name) as cfg:
        with config.compose_service(name, cfg['home']) as svc:
            click.echo(json.dumps(svc.config_dict(), indent=4, sort_keys=True))


@dip.command('uninstall')
@options.NAME
def dip_uninstall(name):
    """ Uninstall CLI by name. """
    with config.config_for(name) as cfg:
        # Bring down service networks
        try:
            with config.compose_project(cfg['home']) as proj:
                proj.networks.remove()
        except exc.DockerComposeProjectError:
            pass

        # Remove executable
        shell.remove(name, cfg['path'])

        # Update config
        config.uninstall(name)

        # Finish
        cname = colored.stylize(name, colors.RED)
        click.echo("Uninstalled {name}".format(name=cname))
