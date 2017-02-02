"""
Helper for file IO.
"""
import os

from . import templates


def write_cli(path, name, home):
    """ Create a CLI.

        Arguments:
            path (str):  Path to executable (ex. /usr/local/bin/fizz)
            name (str):  Name of executable (ex. fizz)
            home (str):  Path to docker-compose.yml
    """
    # Get body of executable
    body = templates.cli(name, home)

    # Write executable
    with open(path, 'w') as executable:
        executable.write(body)

    # chmod 755
    os.chmod(path, 0o755)


def remove_cli(path):
    """ Remove a CLI.

        Arguments:
            path (str):  Path to executable (ex. /usr/local/bin/fizz)
    """
    os.remove(path)
