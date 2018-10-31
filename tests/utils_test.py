import os
import sys
import tempfile

import mock
import pytest
from dip import utils


@mock.patch('dip.utils.pkgpath')
@mock.patch('os.path.exists')
def test_dip_home(mock_exists, mock_pkg):
    mock_exists.return_value = False
    assert utils.dip_home('DIP_HOME') == utils.pkgpath()


@mock.patch('os.path.exists')
def test_dip_home_exists(mock_exists):
    mock_exists.return_value = True
    assert utils.dip_home('DIP_HOME') == os.path.expanduser('~/.dip')


def test_editor():
    if 'EDITOR' in os.environ:
        assert utils.editor() == os.environ['EDITOR']
    else:
        with pytest.raises(KeyError):
            assert utils.editor()


def test_piped_redirected():
    with tempfile.NamedTemporaryFile() as tmp:
        assert utils.piped_redirected(tmp) is True


def test_notty():
    with tempfile.NamedTemporaryFile() as stdin:
        with tempfile.NamedTemporaryFile() as stdout:
            sys.stdin = stdin
            sys.stdout = stdout
            assert utils.notty() is False


@mock.patch('pkg_resources.resource_filename')
def test_pkgpath(mock_filename):
    assert utils.pkgpath() == mock_filename.return_value
