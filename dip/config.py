"""
Dip configuration.
"""
import collections
import os
import re
import subprocess
import time
import sys
from copy import deepcopy

import click
import compose.cli.command
import easysettings
import git
from dip import __version__
from dip import colors
from dip import defaults
from dip import errors
from dip import utils

DEFAULT = {'dips': {},
           'home': defaults.HOME,
           'path': defaults.PATH,
           'version': __version__}


def load(config_path=None):
    """ Load config.json file. """
    # Use supplied path or default
    config_path = config_path or defaults.HOME

    # Read config.json
    try:
        cfg = dict(easysettings.JSONSettings.from_file(config_path))
    except (OSError, IOError, ValueError):
        cfg = {}

    # Merge config with defaults
    return Settings(**utils.deepmerge(deepcopy(DEFAULT), cfg))


class Settings(collections.MutableMapping):
    """ Dip configuration object. """
    def __init__(self, **config):  # pylint: disable=super-init-not-called
        self.config = config
        self.home = config.get('home')
        self.path = config.get('path')
        self.version = config.get('version')

    def __str__(self):
        return self.home

    def __repr__(self):
        return "Settings({self})".format(self=self)

    def __delitem__(self, key):
        del self.config['dips'][key]

    def __getitem__(self, key):
        return Dip(key, **self.config['dips'][key])

    def __iter__(self):
        for key in self.config['dips']:
            yield key

    def __len__(self):
        return len(self.config['dips'])

    def __setitem__(self, key, val):
        self.config['dips'][key] = dict(val)

    # pylint: disable=too-many-arguments
    def install(self, name, home, path, env, remote):
        """ Install config entry. """
        # Update config
        try:
            remote, branch = remote.split('/')
        except (AttributeError, ValueError):
            branch = None
        val = Dip(name, home, path, env, remote, branch)
        self[name] = val
        self.save()

        # Write executable
        try:
            utils.write_exe(path, name)
        except (OSError, IOError):
            raise errors.DipError(
                "Could not write executable for '{name}'".format(name=name))

    def remove(self):
        """ Remove settings file. """
        try:
            os.remove(self.home)
        except (OSError, IOError):
            raise errors.SettingsError(self.home)

    def save(self):
        """ Save config to config.json file. """
        try:
            cfg = easysettings.JSONSettings(**self.config)
            cfg.save(self.home, sort_keys=True)
        except (OSError, IOError):
            raise errors.SettingsError(self.home)

    def uninstall(self, name):
        """ Uninstall config entry. """
        # Remove executable
        try:
            path = os.path.join(self[name].path, name)
            os.remove(path)
        except (OSError, IOError):
            pass

        # Remove network
        try:
            self[name].project.networks.remove()
        except compose.config.errors.ComposeFileNotFound:
            pass

        # Remove config
        del self[name]
        self.save()


class Dip(object):
    """ Dip application object. """
    # pylint: disable=too-many-arguments
    def __init__(self, name, home, path, env=None, remote=None, branch=None):
        self.name = name
        self.home = os.path.abspath(home)
        self.path = os.path.abspath(path)
        self.env = env
        self.remote = remote
        self.branch = branch

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Dip({self})".format(self=self)

    def __iter__(self):
        yield 'home', self.home
        yield 'path', self.path
        yield 'env', self.env or {}
        yield 'remote', self.remote
        yield 'branch', self.branch

    @property
    def repo(self):
        """ Get git repository object. """
        return Repo(self.home, self.remote, self.branch)

    @property
    def project(self):
        """ Get docker-compose project object. """
        return compose.cli.command.get_project(self.home)

    @property
    def service(self):
        """ Get docker-compose service object. """
        return self.project.get_service(self.name)

    @property
    def definition(self):
        """ Get compose file contents as string. """
        for cfg in compose.config.config.get_default_config_files(self.home):
            with open(cfg) as compose_file:
                return compose_file.read()

    def diff(self):
        """ Show git diff between local and remote configurations. """
        self.repo.diff()

    def run(self, *args):
        """ Run CLI. """
        # Build CMD
        cmd = ['docker-compose', 'run', '--rm']
        if utils.notty():
            cmd.append('-T')

        # Get options for docker-compose
        cmd += utils.flatten(['-e', '='.join(x)] for x in self.env.items())

        # Call docker-compose run --rm <args> <svc> $*
        subprocess.call(cmd + [self.name] + list(args),
                        stdout=sys.stdout, stderr=sys.stderr, stdin=sys.stdin)


class Repo(object):
    """ Git repository helper object. """
    def __init__(self, path, remote='origin', branch=None, sleep=10):
        self.path = os.path.abspath(path)
        self.remote_name = remote
        self.branch_name = branch
        self.sleep = sleep

    @property
    def repo(self):
        """ Git repository object. """
        return git.Repo(self.path, search_parent_directories=True)

    @property
    def remote(self):
        """ Git remote object. """
        return self.repo.remote(self.remote_name)

    def paths(self):
        """ Yield remote/local path pairs. """
        for local in compose.config.config.get_default_config_files(self.path):
            expr = r"^({})?/".format(self.repo.working_dir)
            relative = re.sub(expr, '', local)
            remote = "{remote}/{branch}:{rel}".format(remote=self.remote_name,
                                                      branch=self.branch_name,
                                                      rel=relative)
            yield remote, local

    def fetch(self):
        """ Fetch git remote. """
        try:
            self.remote.fetch()
        except git.exc.GitCommandError:
            click.echo(colors.amber('Could not fetch remote'), err=True)

    def diff(self):
        """ Echo diff output and sleep. """
        # Fetch remote
        self.fetch()

        # Echo diff(s)
        for remote, local in self.paths():
            try:
                cmd = ['git', '--no-pager', 'diff', remote, local]
                with open(os.devnull, 'w') as devnull:
                    diff = subprocess.check_output(cmd, stderr=devnull).strip()
                if diff:
                    with utils.newlines():
                        msg = 'Local configuration has diverged from remote:\n'
                        click.echo(colors.amber(msg), err=True)
                        subprocess.call(cmd, stdout=sys.stderr)
                        msg = "\nSleeping for {sleep}s"\
                              .format(sleep=self.sleep)
                        click.echo(msg, err=True)
                    return time.sleep(self.sleep)
            except subprocess.CalledProcessError:
                click.echo(colors.amber("Could not access {remote}"
                                        .format(remote=remote)), err=True)
