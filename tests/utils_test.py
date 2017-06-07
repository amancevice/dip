import os
import sys
import tempfile

from dip import utils


def test_dict_merge():
    dict1 = {'fizz': {'buzz': {'jazz': 'funk', 'hub': 'bub'}}}
    dict2 = {'fizz': {'buzz': {'jazz': 'junk', 'riff': 'raff'}}}
    dict3 = {'buzz': 'fizz'}
    ret = utils.dict_merge(dict1, dict2, dict3)
    exp = {
        'fizz': {
            'buzz': {
                'jazz': 'junk',
                'riff': 'raff',
                'hub': 'bub'
            }
        },
        'buzz': 'fizz'
    }
    assert ret == exp


def test_dict_merge_nondict():
    dict1 = {'fizz': {'buzz': {'jazz': 'funk', 'hub': 'bub'}}}
    dict2 = 42
    ret = utils.dict_merge(dict1, dict2)
    exp = 42
    assert ret == exp


def test_flatten():
    assert utils.flatten([[1, 2, 3], [4, 5, 6]]) == [1, 2, 3, 4, 5, 6]


def test_lreplace():
    assert utils.lreplace('/path/to/relative',
                          '~',
                          '/path/to/relative/location') == '~/location'


def test_piped_redirected():
    with tempfile.NamedTemporaryFile() as tmp:
        assert utils.piped_redirected(tmp) is True


def test_notty():
    with tempfile.NamedTemporaryFile() as stdin:
        with tempfile.NamedTemporaryFile() as stdout:
            sys.stdin = stdin
            sys.stdout = stdout
            assert utils.notty() is False


def test_write_exe():
    with tempfile.NamedTemporaryFile() as tmp:
        path, name = os.path.split(tmp.name)
        utils.write_exe(path, name)
        tmp.flush()
        assert tmp.read() == \
            "#!/bin/bash\ndip run {name} -- $*\n"\
            .format(name=name).encode('utf-8')
        assert os.access(tmp.name, os.X_OK)
