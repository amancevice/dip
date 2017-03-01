"""
Define options for dip commands.
"""
import click
from . import config


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
HOME = click.argument('home', default='.', type=Path())
SERVICE = click.argument('service', type=Service(), nargs=-1)
GLOBAL = click.option('-g', '--global', type=Key(), is_flag=True,
                      help='Global configuration')
PATH_OPT = click.option('-p', '--path', default=CONFIG['path'], type=Path(),
                        help="Path to write executable [default: {}]"
                        .format(CONFIG['path']))
SET = click.option('-s', '--set', help='Set configuration option')
DRY_RUN = click.option('--dry-run', is_flag=True,
                       help='Do not write executable')
