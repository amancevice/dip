"""
Utilities.
"""
import os
import re
import stat
import sys


def contractuser(path):
    """ Shrink user home back to ~ """
    userhome = os.path.expanduser('~')
    userpath = re.sub(r'^{}'.format(userhome), '~', path)
    return userpath


def dip_home(envvar, default='~/.dip'):
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

        # Create home
        path = os.path.expanduser(default)
        os.makedirs(path)
        return path


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
