"""
Dip configuration.
"""
import json
import os
import pkg_resources as pkg

from . import templates


def default():
    """ Default config. """
    return json.loads(templates.config())


def config_path():
    """ Get default path to dip config. """
    # Get path to dip config template
    return pkg.resource_filename(pkg.Requirement.parse('dip'),
                                 'dip/config.json')


def read(path=None):
    """ Get dip config dict. """
    filename = path or config_path()

    # Return default config if no config written
    if not os.path.exists(filename):
        return json.loads(templates.config())

    # Read config.json as dict
    with open(filename, 'r') as cfg:
        return json.loads(cfg.read())


def reset(path=None):
    """ Reset config. """
    filename = path or config_path()
    if os.path.exists(filename):
        os.remove(filename)
    return default()


def write_config(config=None, path=None):
    """ Write default config to path. """
    filename = path or config_path()
    config = config or default()
    body = json.dumps(config, sort_keys=True, indent=4)
    with open(filename, 'w') as cfg:
        cfg.write(body)
