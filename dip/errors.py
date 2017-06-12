"""
dip exceptions
"""
import click


class DipError(click.ClickException):
    """ Generic dip error. """
    pass


class DipConfigError(DipError):
    """ Error accessing dip config. """
    def __init__(self, path):
        super(DipConfigError, self).__init__(
            "Unable to access dip configuration at '{path}'".format(path=path))


class NotInstalledError(DipError):
    """ CLI not installed. """
    def __init__(self, name):
        super(NotInstalledError, self).__init__(
            "'{name}' command is not installed".format(name=name))


class ComposeFileNotFound(DipError):
    """ CLI not installed. """
    def __init__(self, name):
        super(ComposeFileNotFound, self).__init__(
            "No compose file found for '{name}' command".format(name=name))


class NoSuchService(DipError):
    """ CLI not installed. """
    def __init__(self, name):
        super(NoSuchService, self).__init__(
            "No service named '{name}' found in compose file"
            .format(name=name))
