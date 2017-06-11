"""
Define options for dip commands.
"""
import os
import re

import click
from . import __version__


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


ARGS = click.argument('ARGS', nargs=-1)
HOME = click.argument('HOME', callback=expand_home)
KEYS = click.argument('KEYS', is_eager=True, nargs=-1)
NAME = click.argument('NAME', type=Name())
NAMES = click.argument('NAMES', nargs=-1, type=Name())
ENV = click.option('-e', '--env',
                   callback=validate_env,
                   help='Optional ENV variable',
                   multiple=True,
                   type=EnvVal())
GLOBAL = click.option('-g', '--global', 'gbl',
                      help='Get global configuration key',
                      is_flag=True)
SECRET = click.option('-x', '--secret',
                      callback=validate_secret,
                      help='Set secret ENV',
                      multiple=True,
                      type=Env())
PATH = click.option('-p', '--path',
                    help='Path to write executable',
                    type=Path())
REMOTE = click.option('-r', '--remote',
                      help='Optional git remote/branch',
                      type=Name())
VERSION = click.version_option(__version__)
