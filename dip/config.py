"""
Dip configuration.
"""
import contextlib
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


def install(name, home, path, remote, cfgpath=None):
    """ Add dip config to global config. """
    with current(cfgpath) as cfg:
        if remote is None:
            cfg['dips'][name] = {'home': home, 'path': path}
        else:
            cfg['dips'][name] = {'home': home, 'path': path, 'remote': remote}
        write(cfg, cfgpath)


def read(path=None):
    """ Get dip config dict. """
    path = path or PATH
    # Read config.json
    try:
        return dict(easysettings.JSONSettings.from_file(path))
    # Write default if none exists or is bad JSON
    except (OSError, IOError, ValueError):
        return DEFAULT


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
    try:
        cfg = easysettings.JSONSettings()
        cfg.update(config)
        cfg.save(path, sort_keys=True)
    except (OSError, IOError):
        raise exc.DipConfigError(path)
