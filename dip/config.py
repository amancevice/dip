"""
Dip configuration.
"""
import contextlib
import json
import pkg_resources as pkg

import easysettings
from . import exc

PATH = pkg.resource_filename(pkg.Requirement.parse('dip'), 'dip/config.json')
DEFAULT = {'path': '/usr/local/bin', 'dips': {}}


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


def install(name, home, path, cfgpath=None):
    """ Add dip config to global config. """
    with current(cfgpath) as cfg:
        cfg['dips'][name] = {'home': home, 'path': path}
        write(cfg, cfgpath)


def read(path=None):
    """ Get dip config dict. """
    path = path or PATH
    # Read config.json
    try:
        cfg = easysettings.JSONSettings.from_file(path)
    # Write default if none exists or is bad JSON
    except (OSError, IOError, ValueError):
        cfg = easysettings.JSONSettings()
        cfg.update(DEFAULT)
        cfg.save(path)
    return dict(cfg)


def set_path(new_path, path=None):
    """ Set global path config. """
    with current(path) as cfg:
        cfg['path'] = new_path
        write(cfg, path)


def uninstall(name, path=None):
    """ Remove dip config to global config. """
    with current(path) as cfg:
        try:
            del cfg['dips'][name]
            write(cfg, path)
        except KeyError:
            pass


def write(config=None, path=None):
    """ Write default config to path. """
    path = path or PATH
    config = config or DEFAULT
    body = json.dumps(config, sort_keys=True, indent=4)
    try:
        with open(path, 'w') as cfg:
            cfg.write(body)
    except (OSError, IOError):
        raise exc.DipConfigError(path)
