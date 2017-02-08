"""
Define options for dip commands.
"""
import click
from . import config as dipcfg


class Path(click.types.StringParamType):
    """ Override of the StringParamType. """
    NAME = 'PATH'


class Name(click.types.StringParamType):
    """ Override of the StringParamType. """
    NAME = 'NAME'


CONFIG = dipcfg.read()
NAME = click.argument('name', type=Name())
PATH = click.argument('path', type=Path())
HOME = click.argument('home', default='.', type=Path())
PATH_OPT = click.option('--path', default=CONFIG['path'], type=Path(),
                        help="Path to write executable [default: {}]"
                        .format(CONFIG['path']))
DRY_RUN = click.option('--dry-run', is_flag=True,
                       help='Do not write executable')
