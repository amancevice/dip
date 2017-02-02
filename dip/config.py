"""
Dip configuration.
"""
import json
import os
import pkg_resources as pkg

from . import templates


def config_path():
    """ Get default path to dip config. """
    # Get path to dip config template
    return pkg.resource_filename(pkg.Requirement.parse('dip'), 'config.json')


def write_config(path=None, config=None):
    """ Write default config to path. """
    filename = path or config_path()
    body = config or templates.config()
    with open(filename, 'w') as cfg:
        cfg.write(body)


def read(path=None):
    """ Get dip config dict. """
    filename = path or config_path()

    # Return default config if no config written
    if not os.path.exists(filename):
        return json.loads(templates.config())

    # Read config.json as dict
    with open(filename, 'r') as cfg:
        return json.loads(cfg.read())
