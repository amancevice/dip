import contextlib
import json
import pkg_resources as pkg
import tempfile

import mock
import pytest
from dip import config
from dip import exc


@contextlib.contextmanager
def tmpconfig(cfg):
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(json.dumps(cfg, sort_keys=True, indent=4).encode('utf-8'))
        tmp.flush()
        yield tmp


def test_current():
    exp = {'dips': {}, 'path': '/fizz/buzz'}
    with tmpconfig(exp) as tmp:
        with config.current(tmp.name) as ret:
            assert ret == exp


def test_config_for():
    exp = {
        'dips': {'test': {'home': '/tmp', 'path': '/bin'}},
        'path': '/fizz/buzz'}
    with tmpconfig(exp) as tmp:
        with config.config_for('test', tmp.name) as ret:
            assert ret == exp['dips']['test']


def test_config_for_err():
    exp = {'dips': {}, 'path': '/fizz/buzz'}
    with tmpconfig(exp) as tmp:
        with pytest.raises(exc.CliNotInstalled):
            with config.config_for('test') as ret:
                pass


def test_install():
    exp = {'dips': {}, 'path': '/fizz/buzz'}
    with tmpconfig(exp) as tmp:
        config.install('test', '/home', '/path', tmp.name)
        tmp.flush()
        with config.current(tmp.name) as ret:
            exp['dips']['test'] = {'home': '/home', 'path': '/path'}
            assert ret == exp


def test_set_path():
    exp = {'dips': {}, 'path': '/fizz/buzz'}
    with tmpconfig(exp) as tmp:
        config.set_path('/path', tmp.name)
        tmp.flush()
        with config.current(tmp.name) as ret:
            exp['path'] = '/path'
            assert ret == exp


def test_uninstall():
    exp = {
        'dips': {'test': {'home': '/home', 'path': '/path'}},
        'path': '/fizz/buzz'}
    with tmpconfig(exp) as tmp:
        config.uninstall('test', tmp.name)
        tmp.flush()
        with config.current(tmp.name) as ret:
            del exp['dips']['test']
            assert ret == exp


def test_uninstall_err():
    exp = {'dips': {}, 'path': '/fizz/buzz'}
    with tmpconfig(exp) as tmp:
        config.uninstall('test', tmp.name)
        tmp.flush()
        with config.current(tmp.name) as ret:
            assert ret == exp


def test_write():
    cfg = {'dips': {}, 'path': '/fizz/buzz'}
    with tempfile.NamedTemporaryFile() as tmp:
        config.write(cfg, tmp.name)
        tmp.flush()

        ret = tmp.read()
        exp = json.dumps(cfg, sort_keys=True, indent=4).encode('utf-8')
        assert ret == exp


def test_write_err():
    with pytest.raises(exc.DipConfigError):
        config.write({'path': '/path', 'dips': {}}, '/dip')


def test_read_default():
    with tempfile.NamedTemporaryFile() as tmp:
        ret = config.read(tmp.name)
        exp = config.DEFAULT
        assert ret == exp


def test_read():
    cfg = {'dips': {}, 'path': '/fizz/buzz'}
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(json.dumps(cfg, sort_keys=True, indent=4).encode('utf-8'))
        tmp.flush()

        ret = config.read(tmp.name)
        assert ret == cfg


@mock.patch('easysettings.JSONSettings.from_file')
def test_read_oserr(mock_json):
    mock_json.side_effect = OSError
    with tempfile.NamedTemporaryFile() as tmp:
        config.read(tmp.name)
        tmp.flush()

        ret = config.read(tmp.name)
        exp = config.DEFAULT
        assert ret == exp
