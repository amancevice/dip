"""
dip exceptions
"""
import os

import click


class DipError(click.ClickException):
    """ Generic dip error. """
    pass


class DipOSError(DipError):
    """ Error in file IO. """
    def __init__(self, path, name):
        super(DipOSError, self).__init__(
            "Unable to access file at '{path}'"
            .format(path=os.path.join(path, name)))


class DipConfigError(DipError):
    """ Error accessing dip config. """
    def __init__(self, path):
        super(DipConfigError, self).__init__(
            "Unable to access dip configuration at '{path}'".format(path=path))


class CliNotInstalled(DipError):
    """ CLI not in config. """
    def __init__(self, name):
        super(CliNotInstalled, self).__init__(
            "'{name}' is not installed".format(name=name))


class DockerComposeError(DipError):
    """ No docker-compose.yml for CLI in config. """
    def __init__(self, name):
        super(DockerComposeError, self).__init__(
            "No docker-compose.yml definition found for '{name}' command"
            .format(name=name))
