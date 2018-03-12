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


def dip_home(envvar='DIP_HOME'):
    """ Helper to get path to settings.json file. """
    try:
        return os.environ[envvar]
    except KeyError:
        # Find home in order of preference
        homes = ['~/.dip', '/etc/dip', '/usr/local/etc/dip']
        for home in homes:
            path = os.path.expanduser(home)
            if os.path.exists(path):
                return path

        # Use package home as last-resort
        return pkgpath()


def editor():
    """ Helper to get path to EDITOR. """
    return os.environ['EDITOR']


def notty():
    """ Helper to determine if TTY is needed. """
    return not piped_redirected(sys.stdin) and piped_redirected(sys.stdout)


def piped_redirected(stream):
    """ Determine if stream is piped or redirected. """
    mode = os.fstat(stream.fileno()).st_mode
    return stat.S_ISFIFO(mode) or stat.S_ISREG(mode)


def pkgpath():
    """ Helper to return abspath of dip file. """
    root = pkg_resources.Requirement.parse(__package__)
    return pkg_resources.resource_filename(root, __package__)
