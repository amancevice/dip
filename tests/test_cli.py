import os
import tempfile

import mock
from dip import cli
from dip import templates


def test_write_cli():
    name = 'fizz'
    home = '/path/to/docker-compose/'
    with tempfile.NamedTemporaryFile() as tmp:
        path = tmp.name
        cli.write_cli(path, name, home)
        tmp.flush()

        ret = tmp.read()
        exp = templates.cli(name=name, home=home).encode('utf-8')
        assert ret == exp


@mock.patch('os.remove')
def test_remove_cli(mock_rm):
    with tempfile.NamedTemporaryFile() as tmp:
        path = tmp.name
        cli.remove_cli(path)
        mock_rm.assert_called_once_with(path)
