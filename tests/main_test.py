import collections
import contextlib
import json
import os
import tempfile

import click.testing
import dip
import mock
from dip import config
from dip import main


@contextlib.contextmanager
def mock_project():
    svc = mock.MagicMock()
    proj = mock.MagicMock()
    svc.config_dict.return_value = {'key': 'val'}
    proj.get_service.return_value = svc
    yield proj


def test_dip():
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip, [])
    assert result.exit_code == 0


def test_version():
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip, ['--version'])
    assert result.exit_code == 0
    assert result.output == "dip, version {vsn}\n".format(vsn=dip.__version__)


@mock.patch('dip.config.read')
@mock.patch('compose.cli.command.get_project')
def test_show(mock_get, mock_read):
    mock_read.return_value = {
        'dips': {'fizz': {'home': '/home', 'path': '/home/path'}},
        'path': '/usr/local/bin'}
    with mock_project() as mock_proj:
        mock_get.return_value = mock_proj
        runner = click.testing.CliRunner()
        result = runner.invoke(main.dip_show, ['fizz'])
        assert result.exit_code == 0
        assert result.output == json.dumps({'key': 'val'},
                                           indent=4,
                                           sort_keys=True) + '\n'


@mock.patch('dip.shell.write')
@mock.patch('dip.config.write')
def test_install(mock_cli, mock_write):
    name = 'fizz'
    with tempfile.NamedTemporaryFile() as tmppath:
        with tempfile.NamedTemporaryFile() as tmphome:
            path, pathname = os.path.split(tmppath.name)
            home, homename = os.path.split(tmphome.name)
            runner = click.testing.CliRunner()
            result = runner.invoke(main.dip_install, ['--path', path, name, home])
            assert result.exit_code == 0
            assert result.output == "Installed fizz to {path}\n"\
                                    .format(path=path)
            mock_write.assert_called_once_with(name, path)


@mock.patch('dip.shell.write')
@mock.patch('dip.config.write')
def test_install_remote(mock_cli, mock_write):
    name = 'fizz'
    with tempfile.NamedTemporaryFile() as tmppath:
        with tempfile.NamedTemporaryFile() as tmphome:
            path, pathname = os.path.split(tmppath.name)
            home, homename = os.path.split(tmphome.name)
            runner = click.testing.CliRunner()
            result = runner.invoke(
                main.dip_install,
                ['--path', path, '--remote', 'origin', name, home])
            assert result.exit_code == 0
            assert result.output == "Installed fizz to {path}\n"\
                                    .format(path=path)
            mock_write.assert_called_once_with(name, path)


@mock.patch('dip.config.read')
@mock.patch('dip.shell.write')
@mock.patch('dip.config.write')
def test_reinstall(mock_cli, mock_write, mock_read):
    name = 'fizz'
    with tempfile.NamedTemporaryFile() as tmppath:
        with tempfile.NamedTemporaryFile() as tmphome:
            path, pathname = os.path.split(tmppath.name)
            home, homename = os.path.split(tmphome.name)
            mock_read.return_value = {
                'dips': {'fizz': {'home': home, 'path': path}}}
            runner = click.testing.CliRunner()
            result = runner.invoke(main.dip_reinstall, [name])
            assert result.exit_code == 0
            assert result.output == "Reinstalled fizz to {path}\n"\
                                    .format(path=path)
            mock_write.assert_called_once_with(name, path)


@mock.patch('dip.shell.remove')
@mock.patch('dip.config.write')
@mock.patch('dip.config.read')
@mock.patch('dip.config.compose_project')
def test_uninstall(mock_proj, mock_read, mock_write, mock_remove):
    with tempfile.NamedTemporaryFile() as tmp:
        path, tmpname = os.path.split(tmp.name)
        mock_read.return_value = {
            'path': path,
            'dips': {
                'fizz': {
                    'home': '/path/to/fizz',
                    'path': path}}}
        runner = click.testing.CliRunner()
        result = runner.invoke(main.dip_uninstall, ['fizz'])
        assert result.exit_code == 0
        mock_remove.assert_called_once_with('fizz', path)


@mock.patch('dip.shell.remove')
@mock.patch('dip.config.write')
@mock.patch('dip.config.read')
def test_uninstall_no_network(mock_read, mock_write, mock_remove):
    with tempfile.NamedTemporaryFile() as tmp:
        path, tmpname = os.path.split(tmp.name)
        mock_read.return_value = {
            'path': path,
            'dips': {
                'fizz': {
                    'home': '/path/to/fizz',
                    'path': path}}}
        runner = click.testing.CliRunner()
        result = runner.invoke(main.dip_uninstall, ['fizz'])
        assert result.exit_code == 0
        mock_remove.assert_called_once_with('fizz', path)


@mock.patch('os.remove')
def test_uninstall_err(mock_remove):
    mock_remove.side_effect = OSError
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_uninstall, ['fizz'])
    assert result.exit_code == 1


@mock.patch('dip.config.read')
def test_config(mock_read):
    mock_read.return_value = config.DEFAULT
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_config)
    assert result.exit_code == 0
    assert result.output == json.dumps(config.DEFAULT,
                                       sort_keys=True,
                                       indent=4) + '\n'


@mock.patch('dip.config.read')
def test_config_naked(mock_read):
    mock_read.return_value = config.DEFAULT
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_config)
    assert result.exit_code == 0
    assert result.output == json.dumps(config.DEFAULT,
                                       sort_keys=True,
                                       indent=4) + '\n'


@mock.patch('dip.config.read')
def test_config_global_path(mock_read):
    mock_read.return_value = config.DEFAULT
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_config, ['--global', 'path'])
    assert result.exit_code == 0
    assert result.output == '/usr/local/bin\n'


@mock.patch('dip.config.read')
def test_config_dip(mock_read):
    mock_read.return_value = {
        'path': '/path',
        'dips': {
            'dipex': {'home': '/home'}}}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_config, ['dipex', 'home'])
    assert result.exit_code == 0
    assert result.output == '/home\n'


@mock.patch('dip.config.read')
@mock.patch('dip.config.write')
def test_config_global_set(mock_write, mock_read):
    mock_read.return_value = {'path': '/path', 'dips': {}}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_config,
                           ['--global', 'path', '--set', '/fizz'])
    assert result.exit_code == 0
    mock_write.assert_called_once_with({'path': u'/fizz', 'dips': {}})


@mock.patch('dip.config.read')
@mock.patch('dip.config.write')
def test_config_rm(mock_write, mock_read):
    mock_read.return_value = {
        'path': '/path',
        'dips': {
            'test': {
                'remote': None
            }
        }
    }
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_config, ['test', '--rm', 'remote'])
    assert result.exit_code == 0
    mock_write.assert_called_once_with({'path': '/path', 'dips': {'test': {}}})


@mock.patch('dip.config.read')
def test_config_no_key(mock_read):
    mock_read.return_value = {'path': '/path', 'dips': {}}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_config, ['dipex'])
    assert result.exit_code == 1
    assert result.output == ''


@mock.patch('dip.config.read')
def test_config_null_key(mock_read):
    mock_read.return_value = {
        'path': '/path',
        'dips': {
            'dipex': {
                'remote': None
            }
        }
    }
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_config, ['dipex', 'remote'])
    assert result.exit_code == 1
    assert result.output == ''


def test_config_rm_set_err():
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_config,
                           ['test', 'path', '--set', '/fizz', '--rm', 'fizz'])
    assert result.exit_code == 2


def test_config_rm_global_err():
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_config,
                           ['--global', 'path', '--rm', 'path'])
    assert result.exit_code == 2


def test_config_set_no_name_err():
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_config, ['--set', 'path'])
    assert result.exit_code == 2


def test_config_set_no_keys_err():
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_config, ['test', '--set', 'path'])
    assert result.exit_code == 2


@mock.patch('dip.config.read')
@mock.patch('compose.cli.command.get_project')
def test_pull(mock_get, mock_read):
    mock_read.return_value = {'dips': {'test': {'home': '/home'}}}
    with mock_project() as mock_proj:
        mock_get.return_value = mock_proj
        runner = click.testing.CliRunner()
        result = runner.invoke(main.dip_pull, ['test'])
        mock_proj.get_service().pull.assert_called_once_with()


@mock.patch('dip.config.read')
def test_pull_err(mock_read):
    mock_read.return_value = {'dips': {'test': {'home': '/home'}}}
    with mock_project() as mock_proj:
        runner = click.testing.CliRunner()
        result = runner.invoke(main.dip_pull, ['test'])
        assert result.output == \
            "No docker-compose.yml definition found for 'test' command\n"


@mock.patch('dip.config.read')
@mock.patch('compose.cli.command.get_project')
def test_pull_all(mock_get, mock_read):
    mock_read.return_value = {
        'dips': collections.OrderedDict([('test1', {'home': '/home'}),
                                         ('test2', {'home': '/home'})])}
    with mock_project() as mock_proj:
        mock_get.return_value = mock_proj
        runner = click.testing.CliRunner()
        result = runner.invoke(main.dip_pull, ['--all'])
        mock_proj.get_service.assert_has_calls([mock.call('test1'),
                                                mock.call().pull(),
                                                mock.call('test2'),
                                                mock.call().pull()])


@mock.patch('dip.config.read')
def test_env(mock_read):
    mock_read.return_value = {
        'dips': {
            'fizz': {
                'env': {
                    'FIZZ': 'BUZZ',
                    'FUZZ': 'JAZZ'
                }
            }
        }
    }
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_env, ['fizz'])
    assert result.exit_code == 0
    assert result.output in ['-e FIZZ=BUZZ -e FUZZ=JAZZ\n',
                             '-e FUZZ=JAZZ -e FIZZ=BUZZ\n']


@mock.patch('dip.config.read')
def test_env_no_env(mock_read):
    mock_read.return_value = {
        'dips': {
            'fizz': {
                'env': {}
            }
        }
    }
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_env, ['fizz'])
    assert result.exit_code == 0
    assert result.output == ''


@mock.patch('dip.config.read')
def test_env_err(mock_read):
    mock_read.return_value = {'dips': {}}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_env, ['fizz'])
    assert result.exit_code == 1


@mock.patch('dip.config.read')
def test_list_no_dips(mock_read):
    mock_read.return_value = {'dips': {}}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_list)
    assert result.exit_code == 0
    assert result.output == ''


@mock.patch('dip.config.read')
def test_list(mock_read):
    mock_read.return_value = {'dips': {
        'fizz': {'home': '/path/to/fizz'},
        'buzz': {'home': '/path/to/buzz', 'remote': 'origin', 'branch': 'master'},
        'jazz': {'home': '/path/to/jazz', 'remote': 'origin'},
    }}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip_list)
    assert result.exit_code == 0
    assert result.output == '''
buzz /path/to/buzz @ origin/master
fizz /path/to/fizz
jazz /path/to/jazz @ origin

'''
