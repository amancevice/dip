"""
Define options for dip commands.
"""
import os
import re

import click
from . import __version__
from . import config


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
    if value and (ctx.params.get('rm') or ctx.params.get('s_t')):
        raise click.BadOptionUsage("Cannot use both --rm and --set options")

    # Don't allow --rm and --global options
    elif value and param.name == 'rm' and ctx.params['gbl']:
        raise click.BadOptionUsage("Cannot use both --rm and --global options")

    # Validate --set
    elif value and param.name == 's_t' and not ctx.params['gbl']:
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
HOME = click.argument('HOME', default='.', type=Path(), callback=expand_home)
KEYS = click.argument('KEYS', nargs=-1, is_eager=True)
NAME = click.argument('NAME', type=Name())
OPTIONAL_NAME = click.argument('NAME', type=Name(), default='', is_eager=True)
PATH = click.argument('PATH', type=Path())
SERVICE = click.argument('service', nargs=-1)
ENV = click.option('-e', '--env', multiple=True, type=EnvVal(),
                   callback=validate_env, help='Optional ENV variable')
GLOBAL = click.option('-g', '--global', 'gbl', type=Key(), is_eager=True,
                      help='Get global configuration key')
REMOVE = click.option('-r', '--rm', type=Key(),
                      callback=validate_rm_set,
                      help='Remove configuration key')
SECRET = click.option('-x', '--secret', multiple=True, type=Env(),
                      callback=validate_secret, help='Set secret ENV')
PATH_OPT = click.option('-p', '--path', default=CONFIG['path'], type=Path(),
                        help="Path to write executable [default: {}]"
                        .format(CONFIG['path']))
REMOTE = click.option('-r', '--remote', type=Name(),
                      help='Optional git remote name')
SET = click.option('-s', '--set', 's_t', type=Key(),
                   callback=validate_rm_set, help='Set configuration option')
VERSION = click.version_option(__version__)
