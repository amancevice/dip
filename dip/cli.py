"""
Helper for file IO.
"""
import os

from . import exc

TEMPLATE = '''#!/bin/bash

set -e
cd {home}
docker-compose run --rm {name} $*
'''


def write(name, home, path):
    """ Create a CLI.

        Arguments:
            name (str):  Name of executable (ex. fizz)
            home (str):  Path to docker-compose.yml
            path (str):  Path for writing executable (ex. /usr/local/bin)
    """
    # Get body of executable
    body = TEMPLATE.format(home=home, name=name)

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
