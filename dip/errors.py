"""
dip exceptions
"""


class DipError(Exception):
    """ Generic dip error. """
    pass


class SettingsError(DipError):
    """ Error accessing dip config. """
    def __init__(self, path):
        super(SettingsError, self).__init__(
            "Unable to access dip settings at '{path}'".format(path=path))


class NotInstalledError(DipError):
    """ CLI not installed. """
    def __init__(self, name):
        super(NotInstalledError, self).__init__(
            "'{name}' command is not installed".format(name=name))


class NoSuchRemoteError(DipError):
    """ Invalid git repository directory. """
    def __init__(self, name):
        super(NoSuchRemoteError, self).__init__(
            "Remote does not exist '{name}'".format(name=name))


class NoSuchPathError(DipError):
    """ Invalid git repository directory. """
    def __init__(self, path):
        super(NoSuchPathError, self).__init__(
            "Path does not exist '{path}'".format(path=path))


class GitFetchError(DipError):
    """ Error fetching remote. """
    def __init__(self, remote):
        super(GitFetchError, self).__init__(
            "Error fetching remote '{remote}'".format(remote=remote))


class InvalidGitRepositoryError(DipError):
    """ Invalid git repository directory. """
    def __init__(self, path):
        super(InvalidGitRepositoryError, self).__init__(
            "No git repository found in '{path}'".format(path=path))


class ComposeFileNotFound(DipError):
    """ No docker-compose file found. """
    def __init__(self, path):
        super(ComposeFileNotFound, self).__init__(
            "No compose file found in '{path}'".format(path=path))


class NoSuchService(DipError):
    """ No such docker-compose service defined. """
    def __init__(self, name):
        super(NoSuchService, self).__init__(
            "No service named '{name}' found in compose file"
            .format(name=name))
