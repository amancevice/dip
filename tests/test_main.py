import json
import os
import tempfile

import click.testing
import dip
import mock
from dip import config
from dip import main


def test_dip():
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip, [])
    assert result.exit_code == 0


def test_version():
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip, ['--version'])
    assert result.exit_code == 0
    assert result.output == dip.__version__ + '\n'


def test_help():
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip, ['help'])
    assert result.exit_code == 0
    assert result.output == runner.invoke(main.dip, ['--help']).output


@mock.patch('dip.config.read')
def test_show(mock_cfg):
    with tempfile.NamedTemporaryFile() as tmp:
        path, name = os.path.split(tmp.name)
        compose = os.path.join(path, 'docker-compose.yml')
        contents = "version: '2'\n  services:\n    fizz:\n      image: fizz\n"
        with open(compose, 'w') as cmp:
            cmp.write(contents)
        mock_cfg.return_value = {
            'dips': {'fizz': {'home': path, 'path': path}},
            'path': '/usr/local/bin'}
        runner = click.testing.CliRunner()
        result = runner.invoke(main.show, ['fizz'])
        assert result.exit_code == 0
        assert result.output == contents + "\n"


@mock.patch('dip.config.read')
def test_show_ioerr(mock_cfg):
    mock_cfg.return_value = {
        'dips': {'fizz': {'home': '/path/to/fizz', 'path': '/usr/local/bin'}},
        'path': '/usr/local/bin'}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.show, ['fizz'])
    assert result.exit_code == 1
    assert result.output == "Error: No docker-compose.yml definition found "\
                            "for 'fizz' command\n"


@mock.patch('dip.config.read')
def test_show_keyerr(mock_cfg):
    mock_cfg.return_value = {
        'dips': {'fizz': {'home': '/path/to/fizz', 'path': '/usr/local/bin'}},
        'path': '/usr/local/bin'}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.show, ['buzz'])
    assert result.exit_code == 1
    assert result.output == "Error: 'buzz' is not installed\n"


@mock.patch('dip.cli.write')
@mock.patch('dip.config.write')
def test_install(mock_cfg, mock_write):
    name = 'fizz'
    with tempfile.NamedTemporaryFile() as tmppath:
        with tempfile.NamedTemporaryFile() as tmphome:
            path, pathname = os.path.split(tmppath.name)
            home, homename = os.path.split(tmphome.name)
            runner = click.testing.CliRunner()
            result = runner.invoke(main.install, ['--path', path, name, home])
            assert result.exit_code == 0
            assert result.output == "Installed fizz to {path}\n"\
                                    .format(path=path)
            mock_write.assert_called_once_with(name, path)


@mock.patch('dip.cli.write')
@mock.patch('dip.config.write')
def test_install_remote(mock_cfg, mock_write):
    name = 'fizz'
    with tempfile.NamedTemporaryFile() as tmppath:
        with tempfile.NamedTemporaryFile() as tmphome:
            path, pathname = os.path.split(tmppath.name)
            home, homename = os.path.split(tmphome.name)
            runner = click.testing.CliRunner()
            result = runner.invoke(
                main.install,
                ['--path', path, '--remote', 'origin', name, home])
            assert result.exit_code == 0
            assert result.output == "Installed fizz to {path}\n"\
                                    .format(path=path)
            mock_write.assert_called_once_with(name, path)


@mock.patch('dip.cli.remove')
@mock.patch('dip.config.write')
@mock.patch('dip.config.read')
def test_uninstall(mock_cfg, mock_write, mock_remove):
    with tempfile.NamedTemporaryFile() as tmp:
        path, tmpname = os.path.split(tmp.name)
        mock_cfg.return_value = {
            'path': path,
            'dips': {
                'fizz': {
                    'home': '/path/to/fizz',
                    'path': path}}}
        runner = click.testing.CliRunner()
        result = runner.invoke(main.uninstall, ['fizz'])
        assert result.exit_code == 0
        mock_remove.assert_called_once_with('fizz', path)


@mock.patch('os.remove')
def test_uninstall_err(mock_remove):
    mock_remove.side_effect = OSError
    runner = click.testing.CliRunner()
    result = runner.invoke(main.uninstall, ['fizz'])
    assert result.exit_code == 1


@mock.patch('dip.config.read')
def test_config(mock_read):
    mock_read.return_value = config.DEFAULT
    runner = click.testing.CliRunner()
    result = runner.invoke(main.config_)
    assert result.exit_code == 0
    assert result.output == json.dumps(config.DEFAULT,
                                       sort_keys=True,
                                       indent=4) + '\n'


@mock.patch('dip.config.read')
def test_config_global(mock_read):
    mock_read.return_value = config.DEFAULT
    runner = click.testing.CliRunner()
    result = runner.invoke(main.config_, ['--global'])
    assert result.exit_code == 0
    assert result.output == json.dumps(config.DEFAULT,
                                       sort_keys=True,
                                       indent=4) + '\n'


@mock.patch('dip.config.read')
def test_config_global_path(mock_read):
    mock_read.return_value = config.DEFAULT
    runner = click.testing.CliRunner()
    result = runner.invoke(main.config_, ['--global', 'path'])
    assert result.exit_code == 0
    assert result.output == '/usr/local/bin\n'


@mock.patch('dip.config.read')
def test_config_dip(mock_read):
    mock_read.return_value = {
        'path': '/path',
        'dips': {
            'dipex': {'home': '/home'}}}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.config_, ['dipex', 'home'])
    assert result.exit_code == 0
    assert result.output == '/home\n'


@mock.patch('dip.config.read')
@mock.patch('dip.config.write')
def test_config_set(mock_write, mock_read):
    mock_read.return_value = {'path': '/path', 'dips': {}}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.config_,
                           ['--global', 'path', '--set', '/fizz'])
    assert result.exit_code == 0
    mock_write.assert_called_once_with({'path': u'/fizz', 'dips': {}})


@mock.patch('dip.config.read')
def test_config_no_key(mock_read):
    mock_read.return_value = {'path': '/path', 'dips': {}}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.config_, ['dipex'])
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
    result = runner.invoke(main.config_, ['dipex', 'remote'])
    assert result.exit_code == 1
    assert result.output == ''


@mock.patch('dip.config.read')
@mock.patch('os.chdir')
@mock.patch('os.execv')
def test_pull(mock_exe, mock_chd, mock_cfg):
    mock_cfg.return_value = {'dips': {'test': {'home': '/home'}}}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.pull, ['test'])
    mock_chd.assert_called_once_with('/home')
    mock_exe.assert_called_once_with('/usr/local/bin/docker-compose',
                                     ['docker-compose', 'pull', 'test'])


@mock.patch('dip.config.read')
@mock.patch('os.chdir')
@mock.patch('os.execv')
def test_pull_err(mock_exe, mock_chd, mock_cfg):
    mock_cfg.return_value = {'dips': {'test': {'home': '/home'}}}
    mock_exe.side_effect = OSError
    runner = click.testing.CliRunner()
    result = runner.invoke(main.pull, ['test'])
    mock_chd.assert_called_once_with('/home')
    assert result.output == "Error: Unable to pull updates for 'test'\n"


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
    result = runner.invoke(main.env_, ['fizz'])
    assert result.exit_code == 0
    assert result.output in ['-e FIZZ=BUZZ -e FUZZ=JAZZ\n',
                             '-e FUZZ=JAZZ -e FIZZ=BUZZ\n']


@mock.patch('dip.config.read')
def test_env_err(mock_read):
    mock_read.return_value = {'dips': {}}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.env_, ['fizz'])
    assert result.exit_code == 1
