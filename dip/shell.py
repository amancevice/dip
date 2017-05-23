"""
Helper for file IO.
"""
import os

import pkg_resources as pkg
from . import exc


def template(name):
    """ Read the CLI template script. """
    path = pkg.resource_filename(pkg.Requirement.parse('dip'),
                                 'dip/template.sh')
    with open(path, 'r') as temp:
        return temp.read().replace('%%name%%', name)


def write(name, path):
    """ Create a CLI.

        Arguments:
            name   (str):  Name of executable (ex. fizz)
            path   (str):  Path for writing executable (ex. /usr/local/bin)
    """
    # Get body of executable
    body = template(name)

    # Get full path to executable
    fullpath = os.path.join(path, name)

    # Write executable and chmod 0755
    try:
        with open(fullpath, 'w') as exe:
            exe.write(body)
        os.chmod(fullpath, 0o755)
    except (OSError, IOError):
        raise exc.DipOSError(path, name)


def remove(name, path):
    """ Remove a CLI.

        Arguments:
            name (str):  Name of executable (ex. fizz)
            path (str):  Path to executable (ex. /usr/local/bin/fizz)
    """
    try:
        os.remove(os.path.join(path, name))
    except (OSError, IOError):
        raise exc.DipOSError(path, name)
