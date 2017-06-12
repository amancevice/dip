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
    try:
        dip.service
    except compose.config.errors.ComposeFileNotFound:
        raise errors.ComposeFileNotFound(dip.name)
    except compose.project.NoSuchService:
        raise errors.NoSuchService(dip.name)


@contextlib.contextmanager
def lazy_load(ctx, name):
    # Get dip object
    try:
        yield ctx.obj[name]
    except KeyError:
        raise errors.NotInstalledError(name)


@contextlib.contextmanager
def load(ctx, name):
    # Get dip object
    with lazy_load(ctx, name) as dip:
        # Verify dip service state
        verify_service(dip)

        # Move to home
        os.chdir(dip.home)

        # Verify local/remote state
        if dip.remote:
            try:
                dip.repo
                dip.diff()
            except git.exc.InvalidGitRepositoryError:
                click.echo(colors.amber(
                    "'{name}' command has a remote but is not a git repository"
                    .format(name=name)), err=True)

        # Yield dip object
        yield dip


@contextlib.contextmanager
def preload(ctx, name, home, path):
    # Verify dip service state
    verify_service(config.Dip(name, home, path))
    # Yield config
    yield ctx.obj
