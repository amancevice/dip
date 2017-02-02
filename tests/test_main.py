import os
import tempfile

import click.testing
import mock
from dip import main


def test_dip():
    runner = click.testing.CliRunner()
    result = runner.invoke(main.dip, [])
    assert result.exit_code == 0


@mock.patch('dip.cli.write_cli')
def test_install(mock_write):
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
def test_uninstall(mock_remove):
    name = 'fizz'
    with tempfile.NamedTemporaryFile() as tmppath:
        path, pathname = os.path.split(tmppath.name)
        exe = os.path.join(path, name)
        runner = click.testing.CliRunner()
        result = runner.invoke(main.uninstall, ['--path', path, name])
        assert result.exit_code == 0
        mock_remove.assert_called_once_with(exe)
