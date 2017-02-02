"""
Templates for executables.
"""
import json
import os
import pkg_resources as pkg


def cli(name, home):
    """ CLI executable script template. """
    # Get path to dip cli
    template = os.path.join('dip', 'templates', 'cli.sh')
    filename = pkg.resource_filename(pkg.Requirement.parse('dip'), template)

    # Return CLI template body
    with open(filename, 'r') as bash:
        return bash.read().format(name=name, home=home)


def config():
    """ dip config template. """
    cfg = {'path': '/usr/local/bin', 'dips': {}}
    return json.dumps(cfg, sort_keys=True, indent=4)+'\n'
