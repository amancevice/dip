"""
dip contexts.
"""
import collections
import contextlib
import json
import os
import re
import subprocess
import sys
import time

import compose.cli.command
import compose.config
import git as pygit
from dip import errors
from dip import utils

HOME = utils.dip_home('DIP_HOME')
PATH = os.getenv('DIP_PATH', '/usr/local/bin')


class Settings(collections.MutableMapping):
    """ Dip app Settings. """
    # pylint: disable=super-init-not-called
    def __init__(self, *args, **kwargs):
        self.data = dict(*args, **kwargs)
        self.filepath = os.path.join(HOME, 'settings.json')

    def __str__(self):
        return utils.contractuser(self.filepath)

    def __repr__(self):
        return "Settings({self})".format(self=self)

    def __delitem__(self, key):
        del self.data[key]

    def __getitem__(self, key):
        return Dip(**self.data[key])

    def __setitem__(self, key, item):
        self.data[key] = dict(item)

    def __iter__(self):
        for key in self.data:
            yield key

    def __len__(self):
        return len(self.data)

    def install(self, name, home, path=None, env=None, git=None):
        """ Install applicaton. """
        # pylint: disable=too-many-arguments
        app = Dip(name, home, path, env, git)
        try:
            app.install()
        finally:
            self[name] = app
        return app

    def load(self, filepath=None):
        """ Load settings. """
        filepath = filepath or self.filepath
        try:
            with open(filepath) as settings:
                self.data = json.loads(settings.read())
        except (OSError, IOError):
            self.save(filepath)
        except ValueError:
            raise errors.SettingsError(filepath)

    def save(self, filepath=None):
        """ Save settings. """
        filepath = filepath or self.filepath
        try:
            with open(filepath, 'w') as settings:
                settings.write(json.dumps(self.data, indent=4, sort_keys=True))
        except (OSError, IOError, ValueError):
            raise errors.SettingsError(filepath)

    def uninstall(self, name):
        """ Uninstall applicaton. """
        app = self[name]
        app.uninstall()
        del self[name]


class Dip(collections.Mapping):
    """ Dip app. """
    # pylint: disable=super-init-not-called
    def __init__(self, name, home, path=None, env=None, git=None):
        # pylint: disable=too-many-arguments
        self.name = str(name)
        self.home = str(home)
        self.path = path or PATH
        self.env = {k: v for k, v in (env or {}).items() if v}
        self.git = {k: v for k, v in (git or {}).items() if v}

    def __str__(self):
        return self.name

    def __repr__(self):
        return "{self}[{path}]".format(self=self,
                                       path=utils.contractuser(self.home))

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __iter__(self):
        yield 'name'
        yield 'home'
        yield 'path'
        if self.env:
            yield 'env'
        if self.git:
            yield 'git'

    def __len__(self):
        return 3 + bool(self.env) + bool(self.git)

    @property
    def repo(self):
        """ Get git repository object. """
        remote = self.git.get('remote')
        if remote:
            branch = self.git.get('branch')
            sleep = self.git.get('sleep')
            return Repo(self.home, remote, branch, sleep)
        return None

    @property
    def project(self):
        """ Get docker-compose project object. """
        return compose.cli.command.get_project(self.home)

    @property
    def service(self):
        """ Get docker-compose service object. """
        return self.project.get_service(self.name)

    @property
    def definitions(self):
        """ Get compose file contents as string. """
        for cfg in compose.config.config.get_default_config_files(self.home):
            with open(cfg) as compose_file:
                yield compose_file.read()

    def diff(self):
        """ Diff remote configuration. """
        return self.repo and any(self.repo.diffs())

    def install(self):
        """ Write executable. """
        fullpath = os.path.join(self.path, self.name)
        hashbang = "#!/bin/bash"
        command = "dip run {self} -- $@\n".format(self=self)
        with open(fullpath, 'w') as exe:
            exe.write("\n".join([hashbang, command]))
        os.chmod(fullpath, 0o755)

    def run(self, *args):
        """ Run app. """
        # Build CMD
        cmd = ['docker-compose', 'run', '--rm']
        if utils.notty():
            cmd.append('-T')

        # Get options for docker-compose
        cmd += [x for i in self.env.items() for x in ['-e', '='.join(i)]]

        # Call docker-compose run --rm <args> <svc> $*
        with indir(self.home):
            return subprocess.call(cmd + [self.name] + list(args),
                                   stdout=sys.stdout,
                                   stderr=sys.stderr,
                                   stdin=sys.stdin)

    def uninstall(self):
        """ Uninstall executable and bring down network. """
        try:
            os.remove(os.path.join(self.path, self.name))
        except (OSError, IOError):
            pass
        try:
            self.project.networks.remove()
        except compose.config.errors.ConfigurationError:
            pass

    def validate(self, skipgit=False):
        """ Validate git repo and compose project. """
        if not skipgit and self.repo:
            # pylint: disable=no-member
            try:
                assert self.repo.repo
                assert self.repo.remote
            except pygit.exc.NoSuchPathError:
                raise errors.NoSuchPathError(self.home)
            except pygit.exc.InvalidGitRepositoryError:
                raise errors.InvalidGitRepositoryError(self.home)
            except ValueError:
                raise errors.NoSuchRemoteError(self.repo.remotename)

        try:
            assert self.project
            assert self.service
        except compose.config.errors.ComposeFileNotFound:
            raise errors.ComposeFileNotFound(self.home)
        except compose.project.NoSuchService:
            raise errors.NoSuchService(self.name)


class Repo(object):
    """ Git repository for dip app. """

    def __init__(self, path, remote=None, branch=None, sleep=None):
        self.path = os.path.abspath(path)
        self._remote = remote
        self._branch = branch
        self._sleep = sleep

    def __str__(self):
        return self.path

    def __repr__(self):
        return "Repo({self})".format(self=self)

    def __iter__(self):
        if self._remote:
            yield 'remote', self._remote
        if self._branch:
            yield 'branch', self._branch
        if self._sleep:
            yield 'sleep', self._sleep

    @property
    def repo(self):
        """ Git repo object. """
        return pygit.Repo(self.path, search_parent_directories=True)

    @property
    def remote(self):
        """ Git remote object. """
        try:
            return self.repo.remote(self._remote)
        except ValueError:
            raise ValueError(self._remote)

    @property
    def remotename(self):
        """ Name of remote. """
        return self._remote

    @property
    def branch(self):
        """ Git branch name. """
        return self._branch or self.repo.active_branch.name

    @property
    def sleeptime(self):
        """ Time to sleep. """
        return self._sleep or 0

    def diffs(self):
        """ Echo diff output and sleep. """
        # Fetch remote
        # pylint: disable=no-member
        try:
            self.remote.fetch()
        except pygit.exc.GitCommandError:
            raise errors.GitFetchError(self.remotename)

        # Move inside git directory
        paths = compose.config.config.get_default_config_files(self.path)
        # Iterate through docker-compose configurations
        for loc in paths:
            exp = r"^({dir})?/".format(dir=self.repo.working_dir)
            rel = re.sub(exp, '', loc)
            rem = "{remote}/{branch}:{rel}".format(remote=self.remote.name,
                                                   branch=self.branch,
                                                   rel=rel)
            # Yield diff exit code
            cmd = ['git', 'diff', '--exit-code', rem, loc]
            with indir(self.path):
                yield subprocess.call(cmd)

    def pull(self):
        """ Pull from remote. """
        # Pull remote
        with indir(self.path):
            cmd = ['git', 'pull', self.remotename, self.branch]
            subprocess.call(cmd)

    def sleep(self):
        """ Sleep. """
        time.sleep(self.sleeptime)


@contextlib.contextmanager
def indir(path):
    """ Helper to execute git commands in the git project's home. """
    curdir = os.path.abspath(os.path.curdir)
    os.chdir(path)
    yield
    os.chdir(curdir)


@contextlib.contextmanager
def load(filename=None):
    """ Yield read-only settings. """
    settings = Settings()
    settings.load(filename)
    yield settings


@contextlib.contextmanager
def saveonexit(filename=None):
    """ Yield read-only settings. """
    with load(filename) as settings:
        yield settings
        settings.save()


@contextlib.contextmanager
def getapp(name, filename=None, skipgit=False):
    """ Yield read-only settings. """
    with load(filename) as settings:
        try:
            app = settings[name]
        except KeyError:
            raise errors.NotInstalledError(name)

        app.validate(skipgit)
        yield app


@contextlib.contextmanager
def diffapp(name, filename=None):
    """ Yield read-only settings. """
    with getapp(name, filename) as app:
        yield app, app.diff()


def reset(filepath=None):
    """ Remove settings. """
    filepath = filepath or os.path.join(HOME, 'settings.json')
    try:
        os.remove(filepath)
    except (OSError, IOError):
        raise errors.SettingsError(filepath)
