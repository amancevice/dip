"""
Templates for executables.
"""
BASH = '''#!/bin/bash

set -e
cd {pwd}
docker-compose run --rm {exe} $*
'''


def bash(exe, pwd):
    """ Format bash executable script. """
    return BASH.format(exe=exe, pwd=pwd)
