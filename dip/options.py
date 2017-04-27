"""
Define options for dip commands.
"""
import os
import re

import click
from . import __version__
from . import config


def validate_all_or_name(ctx, param, value):
    """ Validate --rm & --set options. """
    # Don't allow --rm and --set options
    if value and (ctx.params.get('all_opt') or ctx.params.get('NAME')):
        raise click.BadOptionUsage("Cannot use both --all option and NAME")
    return value


# pylint: disable=unused-argument
def validate_env(ctx, param, value):
    """ Validate --env option. """
    environment = {}
    for val in value:

        # Export from ENV
        if re.match(r'^[A-Z_]+$', val):
            env = val
            val = os.getenv(val)

        # Export from CLI
        elif re.match(r'^[A-Z_]+=.*$', val):
            env, val = re.split(r'([A-Z_]+)=(.*)', val)[1:-1]

        # Raise Bad usage
        else:
            raise click.BadParameter("Use 'ENV=VALUE', or 'ENV'")
        environment[env] = val
    return environment


def validate_rm_set(ctx, param, value):
    """ Validate --rm & --set options. """
    # Don't allow --rm and --set options
    if value and (ctx.params.get('rm') or ctx.params.get('cfg_set')):
        raise click.BadOptionUsage("Cannot use both --rm and --set options")

    # Don't allow --rm and --global options
    elif value and param.name == 'rm' and ctx.params['gbl']:
        raise click.BadOptionUsage("Cannot use both --rm and --global options")

    # Validate --set
    elif value and param.name == 'cfg_set' and not ctx.params['gbl']:
        if not ctx.params['name']:
            raise click.BadOptionUsage("Cannot use --set without NAME")
        elif not ctx.params['keys']:
            raise click.BadOptionUsage(
                "Cannot use --set without at least one KEY")

    return value


# pylint: disable=unused-argument
def validate_secret(ctx, param, value):
    """ Validate --secret option. """
    for val in value:
        if not re.match(r'^[A-Z_]+$', val):
            raise click.BadParameter("Use 'CAPITALS_AND_UNDERSCORES'")
    return value


# pylint: disable=unused-argument
def expand_home(ctx, param, value):
    """ Expand home argument to absolute path. """
    return os.path.abspath(os.path.expanduser(value))


class Env(click.types.StringParamType):
    """ Override of the StringParamType. """
    name = 'ENV'


class EnvVal(click.types.StringParamType):
    """ Override of the StringParamType. """
    name = 'ENV=VALUE'


class Key(click.types.StringParamType):
    """ Override of the StringParamType. """
    name = 'KEY'


class Path(click.types.StringParamType):
    """ Override of the StringParamType. """
    name = 'PATH'


class Name(click.types.StringParamType):
    """ Override of the StringParamType. """
    name = 'NAME'


CONFIG = config.read()
HOME = click.argument('HOME', callback=expand_home, default='.', type=Path())
KEYS = click.argument('KEYS', is_eager=True, nargs=-1)
NAME = click.argument('NAME', type=Name())
ALL_OR_NAME = click.argument('NAME',
                             callback=validate_all_or_name,
                             default='',
                             type=Name())
OPTIONAL_NAME = click.argument('NAME', default='', is_eager=True, type=Name())
PATH = click.argument('PATH', type=Path())
ENV = click.option('-e', '--env',
                   callback=validate_env,
                   help='Optional ENV variable',
                   multiple=True,
                   type=EnvVal())
GLOBAL = click.option('-g', '--global', 'gbl',
                      help='Get global configuration key',
                      is_eager=True,
                      type=Key())
REMOVE = click.option('-r', '--rm',
                      callback=validate_rm_set,
                      help='Remove configuration key',
                      type=Key())
SECRET = click.option('-x', '--secret',
                      callback=validate_secret,
                      help='Set secret ENV',
                      multiple=True,
                      type=Env())
PATH_OPT = click.option('-p', '--path',
                        default=CONFIG['path'],
                        help="Path to write executable [default: {}]"
                             .format(CONFIG['path']),
                        type=Path())
ALL_OPT = click.option('-a', '--all', 'all_opt',
                       callback=validate_all_or_name,
                       help='Run for all installed dips',
                       is_flag=True)
REMOTE = click.option('-r', '--remote',
                      help='Optional git remote name',
                      type=Name())
CFG_SET = click.option('-s', '--set', 'cfg_set',
                       callback=validate_rm_set,
                       help='Set configuration option',
                       type=Key())
VERSION = click.version_option(__version__)
