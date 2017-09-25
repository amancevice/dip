"""
dip contexts.
"""
import collections
import contextlib
import os
import re
import subprocess
import sys

import compose.cli.command
import compose.config
import easysettings
import git as pygit
from dip import utils


# pylint: disable=too-many-ancestors
class Settings(easysettings.JSONSettings):
    """ Dip Application Settings. """
    HOME = os.getenv('DIP_HOME', utils.pkgpath('settings.json'))
    PATH = os.getenv('DIP_PATH', '/usr/local/bin')
    SLEEP = int(os.getenv('DIP_SLEEP') or '10')

    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(self, *args, **kwargs)
        self.filename = self.HOME

    def __str__(self):
        return self.filename

    def __repr__(self):
        return "Settings({self})".format(self=self)

    def __getitem__(self, key):
        return Dip(**super(Settings, self).__getitem__(key))

    def __setitem__(self, key, item):
        super(Settings, self).__setitem__(key, dict(item))

    # pylint: disable=too-many-arguments
    def install(self, name, home, path=None, env=None, git=None):
        """ Install config entry. """
        app = Dip(name, home, path, env, git)
        try:
            app.install()
        finally:
            self[name] = app
            self.save()
        return app

    def uninstall(self, name):
        """ Uninstall config entry. """
        app = self.pop(name)
        try:
            app.uninstall()
        finally:
            self.save()


# pylint: disable=too-many-ancestors,too-many-arguments
class Dip(collections.Iterable):
    """ Dip Application. """
    def __init__(self, name, home, path=None, env=None, git=None):
        self.name = str(name)
        self.home = str(home)
        self.path = path or Settings.PATH
        self.env = env or {}
        self.git = git or {}

    def __str__(self):
        return self.name

    def __repr__(self):
        return "{self}[{path}]".format(self=self,
                                       path=utils.contractuser(self.home))

    def __iter__(self):
        yield 'name', self.name
        yield 'home', self.home
        yield 'path', self.path
        if self.env:
            yield 'env', self.env
        if self.git:
            yield 'git', dict(self.repo)

    @property
    def repo(self):
        """ Get git repository object. """
        remote = self.git.get('remote')
        branch = self.git.get('branch')
        sleep = self.git.get('sleep')
        return Repo(self.home, remote, branch, sleep)

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
        """ Run application. """
        # Build CMD
        cmd = ['docker-compose', 'run', '--rm']
        if utils.notty():
            cmd.append('-T')

        # Get options for docker-compose
        cmd += utils.flatten(['-e', '='.join(x)] for x in self.env.items())

        # Call docker-compose run --rm <args> <svc> $*
        with indir(self.home):
            return subprocess.call(cmd + [self.name] + list(args),
                                   stdout=sys.stdout,
                                   stderr=sys.stderr,
                                   stdin=sys.stdin)

    def uninstall(self):
        """ Uninstall executable and bring down network. """
        os.remove(os.path.join(self.path, self.name))
        self.project.networks.remove()


class Repo(collections.Iterable):
    """ Git repository for dip application. """
    def __init__(self, path, remote=None, branch=None, sleep=None):
        self.path = os.path.abspath(path)
        self._remote = remote
        self._branch = branch
        self.sleep = sleep

    def __str__(self):
        return self.path

    def __repr__(self):
        return "Repo({self})".format(self=self)

    def __iter__(self):
        if self._remote:
            yield 'remote', self._remote
        if self._branch:
            yield 'branch', self._branch
        if self.sleep:
            yield 'sleep', self.sleep

    @property
    def repo(self):
        """ Git repo object. """
        return pygit.Repo(self.path, search_parent_directories=True)

    @property
    def remote(self):
        """ Git remote object. """
        return self.repo.remote(self._remote)

    @property
    def branch(self):
        """ Git branch name. """
        return self._branch or self.repo.active_branch.name

    def diffs(self):
        """ Echo diff output and sleep. """
        # Fetch remote
        self.remote.fetch()

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
    try:
        settings.load(filename or Settings.HOME)
    except (OSError, IOError):
        settings.save()
    finally:
        yield settings
