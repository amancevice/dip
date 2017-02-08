import json
import os
import tempfile

import click.testing
import mock
from dip import config
from dip import main
from dip import templates


def test_dip():
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip, [])
    assert result.exit_code == 0


def test_help():
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip, ['help'])
    assert result.exit_code == 0
    assert result.output == runner.invoke(main.dip, ['--help']).output


def test_config_help():
    runner = click.testing.CliRunner()
    result = runner.invoke(main.config, ['help'])
    assert result.exit_code == 0
    assert result.output == runner.invoke(main.config, ['--help']).output


@mock.patch('dip.config.read')
def test_home(mock_cfg):
    mock_cfg.return_value = {
        'dips': {'fizz': {'home': '/path/to/fizz', 'path': '/usr/local/bin'}},
        'path': '/usr/local/bin'}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.home_, ['fizz'])
    assert result.exit_code == 0
    assert result.output == '/path/to/fizz\n'


@mock.patch('dip.config.read')
def test_home_err(mock_cfg):
    mock_cfg.return_value = {
        'dips': {'fizz': {'home': '/path/to/fizz', 'path': '/usr/local/bin'}},
        'path': '/usr/local/bin'}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.home_, ['buzz'])
    assert result.exit_code == 1
    assert result.output == "Error: 'buzz' is not installed.\n"


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
        assert result.output == contents+"\n"


@mock.patch('dip.config.read')
def test_show_ioerr(mock_cfg):
    mock_cfg.return_value = {
        'dips': {'fizz': {'home': '/path/to/fizz', 'path': '/usr/local/bin'}},
        'path': '/usr/local/bin'}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.show, ['fizz'])
    assert result.exit_code == 1
    assert result.output == "Error: No docker-compose.yml definition found "\
                            "for 'fizz' command.\n"


@mock.patch('dip.config.read')
def test_show_keyerr(mock_cfg):
    mock_cfg.return_value = {
        'dips': {'fizz': {'home': '/path/to/fizz', 'path': '/usr/local/bin'}},
        'path': '/usr/local/bin'}
    runner = click.testing.CliRunner()
    result = runner.invoke(main.show, ['buzz'])
    assert result.exit_code == 1
    assert result.output == "Error: 'buzz' is not installed.\n"


@mock.patch('dip.cli.write_cli')
@mock.patch('dip.config.write_config')
def test_install(mock_cfg, mock_write):
    name = 'fizz'
    with tempfile.NamedTemporaryFile() as tmppath:
        with tempfile.NamedTemporaryFile() as tmphome:
            path, pathname = os.path.split(tmppath.name)
            home, homename = os.path.split(tmphome.name)
            exe = os.path.join(path, name)
            runner = click.testing.CliRunner()
            result = runner.invoke(main.install, ['--path', path, name, home])
            assert result.exit_code == 0
            assert result.output == "Installed fizz to {exe}\n".format(exe=exe)
            mock_write.assert_called_once_with(exe, name, home)


@mock.patch('dip.cli.remove_cli')
@mock.patch('dip.config.write_config')
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
        exe = os.path.join(path, 'fizz')
        runner = click.testing.CliRunner()
        result = runner.invoke(main.uninstall, ['fizz'])
        assert result.exit_code == 0
        mock_remove.assert_called_once_with(exe)


@mock.patch('dip.cli.remove_cli')
@mock.patch('dip.config.write_config')
@mock.patch('dip.config.read')
def test_uninstall_oserr(mock_cfg, mock_write, mock_remove):
    mock_remove.side_effect = OSError
    with tempfile.NamedTemporaryFile() as tmp:
        path, tmpname = os.path.split(tmp.name)
        mock_cfg.return_value = {
            'path': path,
            'dips': {
                'fizz': {
                    'home': '/path/to/fizz',
                    'path': path}}}
        exe = os.path.join(path, 'fizz')
        runner = click.testing.CliRunner()
        result = runner.invoke(main.uninstall, ['fizz'])
        assert result.exit_code == 1


@mock.patch('dip.cli.remove_cli')
@mock.patch('dip.config.write_config')
@mock.patch('dip.config.read')
def test_uninstall_keyerr(mock_cfg, mock_write, mock_remove):
    with tempfile.NamedTemporaryFile() as tmp:
        path, tmpname = os.path.split(tmp.name)
        mock_cfg.return_value = {'path': path, 'dips': {}}
        exe = os.path.join(path, 'fizz')
        runner = click.testing.CliRunner()
        result = runner.invoke(main.uninstall, ['fizz'])
        assert result.exit_code == 1
        mock_remove.assert_not_called()


def test_config():
    runner = click.testing.CliRunner()
    result = runner.invoke(main.config)
    assert result.exit_code == 0
    assert result.output == templates.config()


@mock.patch('dip.config.write_config')
def test_path(mock_write):
    runner = click.testing.CliRunner()
    result = runner.invoke(main.path_, ['/path/to/bin'])
    exp = config.default()
    exp['path'] = '/path/to/bin'
    assert result.exit_code == 0
    assert result.output == json.dumps(exp, sort_keys=True, indent=4)+'\n'
