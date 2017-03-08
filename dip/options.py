"""
Define options for dip commands.
"""
import os

import click
from . import __version__
from . import config


# pylint: disable=unused-argument
def print_version(ctx, param, value):
    """ Print dip version and exit. """
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


# pylint: disable=unused-argument
def expand_home(ctx, param, value):
    """ Expand home argument to absolute path. """
    return os.path.abspath(os.path.expanduser(value))


class Key(click.types.StringParamType):
    """ Override of the StringParamType. """
    NAME = 'KEY'


class Path(click.types.StringParamType):
    """ Override of the StringParamType. """
    NAME = 'PATH'


class Name(click.types.StringParamType):
    """ Override of the StringParamType. """
    NAME = 'NAME'


class Service(click.types.StringParamType):
    """ Override of the StringParamType. """
    NAME = 'SERVICE'


CONFIG = config.read()
KEYS = click.argument('keys', nargs=-1)
NAME = click.argument('name', type=Name())
PATH = click.argument('path', type=Path())
HOME = click.argument('home', default='.', type=Path(), callback=expand_home)
SERVICE = click.argument('service', type=Service(), nargs=-1)
GLOBAL = click.option('-g', '--global', type=Key(), is_flag=True,
                      help='Global configuration')
PATH_OPT = click.option('-p', '--path', default=CONFIG['path'], type=Path(),
                        help="Path to write executable [default: {}]"
                        .format(CONFIG['path']))
SET = click.option('-s', '--set', help='Set configuration option')
REMOTE = click.option('-r', '--remote', help='Optional git remote name')
DRY_RUN = click.option('--dry-run', is_flag=True,
                       help='Do not write executable')
VERSION = click.option('-v', '--version', is_flag=True, is_eager=True,
                       callback=print_version, help='Print dip version')
