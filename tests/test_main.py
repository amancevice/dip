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
def test_uninstall(mock_cfg, mock_remove):
    name = 'fizz'
    with tempfile.NamedTemporaryFile() as tmppath:
        path, pathname = os.path.split(tmppath.name)
        exe = os.path.join(path, name)
        runner = click.testing.CliRunner()
        result = runner.invoke(main.uninstall, ['--path', path, name])
        assert result.exit_code == 0
        mock_remove.assert_called_once_with(exe)


@mock.patch('dip.cli.remove_cli')
@mock.patch('dip.config.write_config')
def test_uninstall_os_err(mock_cfg, mock_remove):
    mock_remove.side_effect = OSError
    name = 'fizz'
    with tempfile.NamedTemporaryFile() as tmppath:
        path, pathname = os.path.split(tmppath.name)
        exe = os.path.join(path, name)
        runner = click.testing.CliRunner()
        result = runner.invoke(main.uninstall, ['--path', path, name])
        assert result.exit_code == 1
        mock_remove.assert_called_once_with(exe)


@mock.patch('dip.cli.remove_cli')
@mock.patch('dip.config.write_config')
def test_uninstall_key_err(mock_cfg, mock_remove):
    name = 'fizz'
    with tempfile.NamedTemporaryFile() as tmppath:
        path, pathname = os.path.split(tmppath.name)
        exe = os.path.join(path, name)
        runner = click.testing.CliRunner()
        result = runner.invoke(main.uninstall, ['--path', path, name])
        assert result.exit_code == 0
        mock_remove.assert_called_once_with(exe)
        mock_cfg.assert_not_called


@mock.patch('dip.cli.remove_cli')
@mock.patch('dip.config.write_config')
def test_uninstall_no_key_err(mock_cfg, mock_remove):
    name = 'fizz'
    with tempfile.NamedTemporaryFile() as tmppath:
        with tempfile.NamedTemporaryFile() as tmphome:
            path, pathname = os.path.split(tmppath.name)
            home, homename = os.path.split(tmphome.name)
            exe = os.path.join(path, name)

            # Install fizz
            runner = click.testing.CliRunner()
            result = runner.invoke(main.install, ['--path', path, name, home])

            # Uninstall fizz
            runner = click.testing.CliRunner()
            result = runner.invoke(main.uninstall, ['--path', path, name])
            assert result.exit_code == 0
            mock_remove.assert_called_once_with(exe)
            mock_cfg.assert_called_with(config.default())


def test_show():
    runner = click.testing.CliRunner()
    result = runner.invoke(main.show)
    assert result.exit_code == 0
    assert result.output == templates.config()


@mock.patch('dip.config.reset')
def test_reset(mock_reset):
    mock_reset.return_value = config.default()
    runner = click.testing.CliRunner()
    result = runner.invoke(main.reset)
    assert result.exit_code == 0
    assert result.output == templates.config()


@mock.patch('dip.config.write_config')
def test_set(mock_write):
    runner = click.testing.CliRunner()
    result = runner.invoke(main.set, ['fizz', 'buzz'])
    exp = config.default()
    exp['fizz'] = 'buzz'
    assert result.exit_code == 0
    assert result.output == json.dumps(exp, sort_keys=True, indent=4)+'\n'
