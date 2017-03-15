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
    """ Validate ENV=VALUE. """
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


# pylint: disable=unused-argument
def validate_secret(ctx, param, value):
    """ Validate ENV=VALUE. """
    for val in value:
        if not re.match(r'^[A-Z_]+$', val):
            raise click.BadParameter("Use 'CAPITALS_AND_UNDERSCORES'")
    return value


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


class Env(click.types.StringParamType):
    """ Override of the StringParamType. """
    name = 'env'


class EnvVal(click.types.StringParamType):
    """ Override of the StringParamType. """
    name = 'env=value'


class Key(click.types.StringParamType):
    """ Override of the StringParamType. """
    name = 'key'


class Path(click.types.StringParamType):
    """ Override of the StringParamType. """
    name = 'path'


class Name(click.types.StringParamType):
    """ Override of the StringParamType. """
    name = 'name'


CONFIG = config.read()
HOME = click.argument('home', default='.', type=Path(), callback=expand_home)
KEYS = click.argument('keys', nargs=-1)
NAME = click.argument('name', type=Name())
PATH = click.argument('path', type=Path())
SERVICE = click.argument('service', nargs=-1)
ENV = click.option('-e', '--env', multiple=True, type=EnvVal(),
                   callback=validate_env, help='Optional ENV variable')
GLOBAL = click.option('-g', '--global', type=Key(), is_flag=True,
                      help='Global configuration')
SECRET = click.option('-x', '--secret', multiple=True, type=Env(),
                      callback=validate_secret, help='Set secret ENV')
PATH_OPT = click.option('-p', '--path', default=CONFIG['path'], type=Path(),
                        help="Path to write executable [default: {}]"
                        .format(CONFIG['path']))
REMOTE = click.option('-r', '--remote', type=Name(),
                      help='Optional git remote name')
SET = click.option('-s', '--set', help='Set configuration option')
VERSION = click.option('-v', '--version', is_flag=True, is_eager=True,
                       callback=print_version, help='Print dip version')
