from dip import templates


def test_bash():
    ret = templates.bash('fizz', '/path/to/buzz')
    exp = '''#!/bin/bash

set -e
cd /path/to/buzz
docker-compose run --rm fizz $*
'''
    assert ret == exp
