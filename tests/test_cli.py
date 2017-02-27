import os
import tempfile

import mock
import pytest
from dip import cli
from dip import exc


def test_write():
    with tempfile.NamedTemporaryFile() as tmp:
        path, name = os.path.split(tmp.name)
        cli.write(name, path)
        tmp.flush()

        ret = tmp.read()
        exp = cli.template(name).encode('utf-8')
        assert ret == exp


def test_write_remote():
    with tempfile.NamedTemporaryFile() as tmp:
        path, name = os.path.split(tmp.name)
        cli.write(name, path)
        tmp.flush()

        ret = tmp.read()
        exp = cli.template(name).encode('utf-8')
        assert ret == exp


def test_write_err():
    with pytest.raises(exc.DipOSError):
        cli.write('fizz', '/dip')


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
