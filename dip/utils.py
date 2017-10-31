"""
Utilities.
"""
import os
import re
import stat
import sys

import pkg_resources


def contractuser(path):
    """ Shrink user home back to ~ """
    userhome = os.path.expanduser('~')
    userpath = re.sub(r'^{}'.format(userhome), '~', path)
    return userpath


def editor():
    """ Helper to get path to EDITOR. """
    return os.environ['EDITOR']


def notty():
    """ Helper to determine if TTY is needed. """
    return not piped_redirected(sys.stdin) and piped_redirected(sys.stdout)


def pkgpath(filename):
    """ Helper to return abspath of dip file. """
    path = os.path.join(__package__, filename)
    root = pkg_resources.Requirement.parse(__package__)
    return pkg_resources.resource_filename(root, path)


def piped_redirected(stream):
    """ Determine if stream is piped or redirected. """
    mode = os.fstat(stream.fileno()).st_mode
    return stat.S_ISFIFO(mode) or stat.S_ISREG(mode)
