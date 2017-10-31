import os
import sys
import tempfile

import pytest
from dip import utils


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
