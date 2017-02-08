"""
dip exceptions
"""
import click


class DipError(click.ClickException):
    """ Generic dip error. """
    pass


class CliNotInstalled(DipError):
    """ CLI not in config. """
    def __init__(self, name):
        super(CliNotInstalled, self).__init__(
            "'{name}' is not installed.".format(name=name))


class DockerComposeError(DipError):
    """ No docker-compose.yml for CLI in config. """
    def __init__(self, name):
        super(DockerComposeError, self).__init__(
            "No docker-compose.yml definition found for '{name}' command."
            .format(name=name))
