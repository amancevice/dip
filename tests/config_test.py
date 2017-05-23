import contextlib
import json
import pkg_resources as pkg

import compose
import mock
import pytest
from dip import config
from dip import exc


@mock.patch('dip.config.read')
def test_current(mock_read):
    exp = {
        'dips': {},
        'home': '/home',
        'path': '/fizz/buzz',
        'version': '0.0.0'
    }
    mock_read.return_value = exp
    with config.current() as ret:
        assert ret == exp


@mock.patch('dip.config.read')
def test_config_for(mock_read):
    exp = {
        'dips': {'test': {'home': '/tmp', 'path': '/bin'}},
        'home': '/home',
        'path': '/fizz/buzz',
        'version': '0.0.0'
    }
    mock_read.return_value = exp
    with config.config_for('test') as ret:
        assert ret == exp['dips']['test']


@mock.patch('dip.config.read')
def test_config_for_err(mock_read):
    exp = {
        'dips': {},
        'home': '/home',
        'path': '/fizz/buzz',
        'version': '0.0.0'
    }
    mock_read.return_value = exp
    with pytest.raises(exc.CliNotInstalled):
        with config.config_for('test') as ret:
            pass


@mock.patch('compose.cli.command.get_project')
def test_compose_project(mock_proj):
    proj = mock.MagicMock()
    mock_proj.return_value = proj
    with config.compose_project('/path/to/project') as proj:
        mock_proj.assert_called_once_with('/path/to/project')


def test_compose_project_err():
    with pytest.raises(exc.DockerComposeProjectError):
        with config.compose_project('/path/to/project') as proj:
            pass


@mock.patch('compose.cli.command.get_project')
def test_compose_service(mock_proj):
    proj = mock.MagicMock()
    mock_proj.return_value = proj
    with config.compose_service('mysvc', '/path/to/project') as svc:
        mock_proj.assert_called_once_with('/path/to/project')
        proj.get_service.assert_called_once_with('mysvc')


@mock.patch('compose.cli.command.get_project')
def test_compose_service_err(mock_proj):
    mock_proj.side_effect = compose.config.errors.ConfigurationError('err')
    with pytest.raises(exc.DockerComposeServiceError):
        with config.compose_service('mysvc', '/path/to/project') as svc:
            pass


@mock.patch('dip.config.write')
@mock.patch('dip.config.read')
def test_install(mock_read, mock_write):
    exp = {
        'dips': {},
        'home': '/home',
        'path': '/fizz/buzz',
        'version': '0.0.0'
    }
    mock_read.return_value = exp
    config.install('test', '/home', '/path', None, {})
    mock_write.assert_called_once_with({
        'dips': {
            'test': {
                'home': '/home',
                'path': '/path',
                'remote': None,
                'branch': None,
                'env': {}
            }
        },
        'home': '/home',
        'path': '/fizz/buzz',
        'version': '0.0.0'
    }, None)


@mock.patch('dip.config.write')
@mock.patch('dip.config.read')
def test_install_remote(mock_read, mock_write):
    exp = {
        'dips': {},
        'home': '/home',
        'path': '/fizz/buzz',
        'version': '0.0.0'
    }
    mock_read.return_value = exp
    config.install('test', '/home', '/path', 'origin', {})
    mock_write.assert_called_once_with({
        'dips': {
            'test': {
                'home': '/home',
                'path': '/path',
                'remote': 'origin',
                'branch': None,
                'env': {}
            }
        },
        'home': '/home',
        'path': '/fizz/buzz',
        'version': '0.0.0'
    }, None)


@mock.patch('dip.config.write')
@mock.patch('dip.config.read')
def test_uninstall(mock_read, mock_write):
    exp = {
        'dips': {'test': {'home': '/home', 'path': '/path'}},
        'home': '/home',
        'path': '/fizz/buzz',
        'version': '0.0.0'
    }
    mock_read.return_value = exp
    config.uninstall('test')
    mock_write.assert_called_once_with({
        'dips': {},
        'home': '/home',
        'path': '/fizz/buzz',
        'version': '0.0.0'
    }, None)


@mock.patch('dip.config.read')
@mock.patch('sys.exit')
def test_uninstall_err(mock_exit, mock_read):
    exp = {
        'dips': {},
        'home': '/home',
        'path': '/fizz/buzz',
        'version': '0.0.0'
    }
    mock_read.return_value = exp
    config.uninstall('test')
    mock_exit.assert_called_once_with(1)


@mock.patch('dip.config.read')
@mock.patch('easysettings.JSONSettings.save')
@mock.patch('easysettings.JSONSettings.update')
def test_write(mock_update, mock_save, mock_read):
    exp = {
        'dips': {},
        'home': '/home',
        'path': '/fizz/buzz',
        'version': '0.0.0'
    }
    mock_read.return_value = exp
    config.write(exp)
    mock_update.assert_called_once_with(exp)
    mock_save.assert_called_once_with(config.PATH, sort_keys=True)


def test_write_err():
    with pytest.raises(exc.DipConfigError):
        config.write({'path': '/path', 'dips': {}}, '/dip')


@mock.patch('easysettings.JSONSettings.from_file')
def test_read(mock_from_file):
    exp = {
        'dips': {},
        'home': '/home',
        'path': '/fizz/buzz',
        'version': '0.0.0'
    }
    mock_from_file.return_value = exp
    ret = config.read()
    assert ret == exp


@mock.patch('easysettings.JSONSettings.from_file')
def test_read_oserr(mock_from_file):
    mock_from_file.side_effect = OSError
    ret = config.read()
    exp = config.DEFAULT
    assert ret == exp


def test_dict_merge():
    dict1 = {'fizz': {'buzz': {'jazz': 'funk', 'hub': 'bub'}}}
    dict2 = {'fizz': {'buzz': {'jazz': 'junk', 'riff': 'raff'}}}
    dict3 = {'buzz': 'fizz'}
    ret = config.dict_merge(dict1, dict2, dict3)
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
    ret = config.dict_merge(dict1, dict2)
    exp = 42
    assert ret == exp
