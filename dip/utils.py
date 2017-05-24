"""
Utilities.
"""
import contextlib
import os
from copy import deepcopy

import click
import pkg_resources


@contextlib.contextmanager
def newlines(iterable):
    """ Helper to wrap output in newlines. """
    empty = not any(iterable)
    if not empty:
        click.echo()
    yield
    if not empty:
        click.echo()


def dict_merge(target, *args):
    """ Taken from: http://blog.impressiver.com/post/31434674390 """
    # Merge multiple dicts
    if len(args) > 1:
        for obj in args:
            dict_merge(target, obj)
        return target

    # Recursively merge dicts and set non-dict values
    obj = args[0]
    if not isinstance(obj, dict):
        return obj
    for key, val in obj.items():
        if key in target and isinstance(target[key], dict):
            dict_merge(target[key], val)
        else:
            target[key] = deepcopy(val)
    return target


def flatten(items):
    """ Flatten a list of lists. """
    return [y for x in items for y in x]


def abspath(*path):
    """ Helper to return abspath of dip file. """
    path = os.path.join(*path)
    root = pkg_resources.Requirement.parse(__package__)
    return pkg_resources.resource_filename(root, path)
