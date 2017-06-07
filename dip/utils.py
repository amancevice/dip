"""
Utilities.
"""
import contextlib
import os
import re
import stat
import sys
from copy import deepcopy

import click
import pkg_resources


@contextlib.contextmanager
def newlines(echo=True):
    """ Helper to wrap output in newlines. """
    if echo:
        click.echo()
    yield
    if echo:
        click.echo()


def abspath(filename):
    """ Helper to return abspath of dip file. """
    path = os.path.join(__package__, filename)
    root = pkg_resources.Requirement.parse(__package__)
    return pkg_resources.resource_filename(root, path)


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


def lreplace(search, replace, string):
    """ Left-replace. """
    return re.sub(r"^{search}".format(search=search), replace, string)


def notty():
    """ Helper to determine if TTY is needed. """
    return not piped_redirected(sys.stdin) and piped_redirected(sys.stdout)


def piped_redirected(stream):
    """ Determine if stream is piped or redirected. """
    mode = os.fstat(stream.fileno()).st_mode
    return stat.S_ISFIFO(mode) or stat.S_ISREG(mode)


def write_exe(path, name):
    """ Write executable to path. """
    fullpath = os.path.join(path, name)
    with open(fullpath, 'w') as exe:
        exe.write("#!/bin/bash\ndip run {name} -- $*\n".format(name=name))
    os.chmod(fullpath, 0o755)
