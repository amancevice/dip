import os
import tempfile

import mock
import pytest
from dip import cli
from dip import exc


def test_write():
    home = '/path/to/docker-compose/'
    with tempfile.NamedTemporaryFile() as tmp:
        path, name = os.path.split(tmp.name)
        cli.write(name, home, path)
        tmp.flush()

        ret = tmp.read()
        exp = cli.TEMPLATE.format(name=name, home=home).encode('utf-8')
        assert ret == exp


def test_write_err():
    with pytest.raises(exc.DipOSError):
        cli.write('fizz', '/buzz', '/dip')


@mock.patch('os.remove')
def test_remove(mock_rm):
    with tempfile.NamedTemporaryFile() as tmp:
        path, name = os.path.split(tmp.name)
        cli.remove(name, path)
        mock_rm.assert_called_once_with(tmp.name)


@mock.patch('os.remove')
def test_remove_err(mock_rm):
    mock_rm.side_effect = OSError
    with pytest.raises(exc.DipOSError):
        cli.remove('fizz', '/buzz')
