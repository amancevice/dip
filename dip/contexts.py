"""
dip contexts.
"""
import contextlib
import os

import click
import compose
import git
from . import colors
from . import config
from . import errors


def verify_service(dip):
    """ Verify a docker-compose service is usable. """
    try:
        dip.service
    except compose.config.errors.ComposeFileNotFound:
        raise errors.ComposeFileNotFound(dip.name)
    except compose.project.NoSuchService:
        raise errors.NoSuchService(dip.name)


@contextlib.contextmanager
def lazy_load(ctx, name):
    """ Load dip object without validating it. """
    # Get dip object
    try:
        yield ctx.obj[name]
    except KeyError:
        raise errors.NotInstalledError(name)


@contextlib.contextmanager
def load(ctx, name):
    """ Load dip object and validate its state. """
    # Get dip object
    with lazy_load(ctx, name) as dip:
        # Verify dip service state
        verify_service(dip)

        # Move to home
        os.chdir(dip.home)

        # Verify local/remote state
        if dip.remote:
            try:
                dip.repo and dip.diff()
            except git.exc.InvalidGitRepositoryError:
                click.echo(colors.amber(
                    "'{name}' command has a remote but is not a git repository"
                    .format(name=name)), err=True)

        # Yield dip object
        yield dip


@contextlib.contextmanager
def preload(ctx, name, home, path):
    """ Load a dip object and validate it is usable. """
    # Verify dip service state
    verify_service(config.Dip(name, home, path))
    # Yield config
    yield ctx.obj
