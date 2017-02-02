import json

from dip import templates


def test_cli():
    ret = templates.cli('fizz', '/path/to/buzz')
    exp = '''#!/bin/bash

set -e
cd /path/to/buzz
docker-compose run --rm fizz $*
'''
    assert ret == exp


def test_config():
    ret = templates.config()
    exp = json.dumps({
        'path': '/usr/local/bin',
        'dips': []}, sort_keys=True, indent=4)
    assert ret == exp
