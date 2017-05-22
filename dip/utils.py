"""
Utilities.
"""
import contextlib

import click


@contextlib.contextmanager
def newlines(iterable):
    """ Helper to wrap output in newlines. """
    empty = not any(iterable)
    if not empty:
        click.echo()
    yield
    if not empty:
        click.echo()
