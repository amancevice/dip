"""
Dip configuration.
"""
import contextlib
import functools
import sys
from copy import deepcopy

import compose
import easysettings
import pkg_resources as pkg
from compose.cli import command
from . import __version__
from . import exc

PATH = pkg.resource_filename(pkg.Requirement.parse('dip'), 'dip/config.json')
DEFAULT = {
    'dips': {},
    'home': PATH,
    'path': '/usr/local/bin',
    'version': __version__
}


@contextlib.contextmanager
def current(path=None):
    """ Context manager for dip configurations. """
    yield read(path)


@contextlib.contextmanager
def config_for(name, path=None):
    """ Context manager for dip configurations. """
    with current(path) as cfg:
        try:
            yield cfg['dips'][name]
        except KeyError:
            raise exc.CliNotInstalled(name)


@contextlib.contextmanager
def compose_service(name, *args, **kwargs):
    try:
        proj = command.get_project(*args, **kwargs)
        svc = proj.get_service(name)
        yield svc
    except compose.config.errors.ConfigurationError:
        raise exc.DockerComposeError(name)


def dict_merge(target, *args):
    """ Taken from: http://blog.impressiver.com/post/31434674390 """
    # Merge multiple dicts
    if len(args) > 1:
        for obj in args:
            dict_merge(target, obj)
        return target

    # Recursively merge dicts and set non-dict values
    obj = args[0]
    if not isinstance(obj, dict):
        return obj
    for key, val in obj.items():
        if key in target and isinstance(target[key], dict):
            dict_merge(target[key], val)
        else:
            target[key] = deepcopy(val)
    return target


# pylint: disable=too-many-arguments
def install(name, home, path, remote, env, cfgpath=None):
    """ Add dip config to global config. """
    with current(cfgpath) as cfg:
        try:
            remote, branch = remote.split('/')
        except (ValueError, AttributeError):
            branch = None
        cfg['dips'][name] = {'home': home,
                             'path': path,
                             'remote': remote,
                             'branch': branch,
                             'env': env}
        write(cfg, cfgpath)


def read(path=None):
    """ Get dip config dict. """
    path = path or PATH
    # Read config.json
    try:
        cfg = dict(easysettings.JSONSettings.from_file(path))
        return dict_merge(deepcopy(DEFAULT), cfg)
    # Write default if none exists or is bad JSON
    except (OSError, IOError, ValueError):
        return DEFAULT


def set_config(cfg, keys, value):
    """ Helper to set a config value.

        Arguments:
            cfg   (dict):   Current configuration
            keys  (tuple):  Path to target key
            value (str):    New value to set
    """
    upd = functools.reduce(lambda x, y: {y: x}, reversed(keys), value)
    new_cfg = dict_merge(cfg, upd)
    write(new_cfg)


def get_config(cfg, keys):
    """ Helper to get a config value.

        Arguments:
            cfg   (dict):   Current configuration
            keys  (tuple):  Path to target key
            value (str):    New value to set
    """
    return functools.reduce(lambda x, y: x[y], keys, cfg)


def rm_config(cfg, keys, value):
    """ Helper to remove a config value.

        Arguments:
            cfg   (dict):   Current configuration
            keys  (tuple):  Path to target key
            value (str):    New value to set
    """
    del get_config(cfg, keys)[value]
    write(cfg)


def uninstall(name, path=None):
    """ Remove dip config to global config. """
    with current(path) as cfg:
        try:
            del cfg['dips'][name]
            write(cfg, path)
        except KeyError:
            sys.exit(1)


def write(config=None, path=None):
    """ Write default config to path. """
    path = path or PATH
    config = config or DEFAULT
    try:
        cfg = easysettings.JSONSettings()
        cfg.update(config)
        cfg['version'] = __version__
        cfg.save(path, sort_keys=True)
    except (OSError, IOError):
        raise exc.DipConfigError(path)
