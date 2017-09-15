import contextlib
import json
from copy import deepcopy

import click.testing
import dip
import mock
from dip import errors
from dip import main
from . import CONFIG

dip.defaults.PATH = CONFIG.path


@contextlib.contextmanager
def invoke(command, args=None):
    runner = click.testing.CliRunner()
    yield runner.invoke(command, args or [], obj=deepcopy(CONFIG))


def test_dip():
    with invoke(main.dip) as result:
        assert result.exit_code == 0


def test_version():
    with invoke(main.dip, ['--version']) as result:
        assert result.exit_code == 0
        assert result.output == \
            "dip, version {vsn}\n".format(vsn=dip.__version__)


def test_config_string():
    with invoke(main.dip_config, ['fizz', 'env', 'FIZZ']) as result:
        assert result.exit_code == 0
        assert result.output == \
            CONFIG.config['dips']['fizz']['env']['FIZZ'] + '\n'


def test_config_json():
    with invoke(main.dip_config, ['fizz']) as result:
        assert result.exit_code == 0
        assert result.output == json.dumps(CONFIG.config['dips']['fizz'],
                                           indent=4,
                                           sort_keys=True) + '\n'


def test_config_global():
    with invoke(main.dip_config, ['--global', 'home']) as result:
        assert result.exit_code == 0
        assert result.output == CONFIG.config['home'] + '\n'


def test_config_err():
    with invoke(main.dip_config, ['--global', 'fizz']) as result:
        assert result.exit_code == 1


@mock.patch('dip.config.Settings.install')
@mock.patch('dip.contexts.verify_service')
def test_install(mock_svc, mock_ins):
    with invoke(main.dip_install, ['fizz', '/test/path',
                                   '--env', 'FIZZ=BUZZ',
                                   '--remote', 'origin/master']):
        mock_ins.assert_called_once_with('fizz', '/test/path', '/path/to/bin',
                                         {'FIZZ': 'BUZZ'}, 'origin/master')


def test_list():
    with invoke(main.dip_list) as result:
        assert result.exit_code == 0
        assert result.output == '''
buzz /path/to/buzz @ origin
fizz /path/to/fizz @ origin/master
jazz /path/to/jazz

'''


@mock.patch('dip.contexts.load')
def test_pull(mock_load):
    with invoke(main.dip_pull, ['fizz']) as result:
        mock_load.return_value.__enter__\
            .return_value.service.pull.assert_called_once_with()
        assert result.exit_code == 0


@mock.patch('dip.contexts.load')
def test_pull_err(mock_load):
    mock_load.return_value.__enter__\
        .return_value.service.pull.side_effect = Exception
    with invoke(main.dip_pull, ['fizz']) as result:
        mock_load.return_value.__enter__\
            .return_value.service.pull.assert_called_once_with()
        assert result.exit_code == 1


@mock.patch('dip.contexts.load')
def test_pull_dip_err(mock_load):
    mock_load.return_value.__enter__.side_effect = errors.DipError('FizzBuzz')
    with invoke(main.dip_pull, ['fizz']) as result:
        assert result.exit_code == 1


@mock.patch('dip.contexts.load')
def test_run(mock_load):
    with invoke(main.dip_run, ['fizz', '--',
                               '--opt1', 'val1',
                               '--flag']) as result:
        mock_load.return_value.__enter__\
            .return_value.run\
            .assert_called_once_with('--opt1', 'val1', '--flag')
        assert result.exit_code == 0


@mock.patch('dip.contexts.load')
def test_show(mock_load):
    mock_load.return_value.__enter__.return_value.definition = 'TEST'
    with invoke(main.dip_show, ['fizz']) as result:
        assert result.exit_code == 0
        assert result.output == '\nTEST\n\n'


@mock.patch('dip.config.Settings.uninstall')
@mock.patch('dip.contexts.lazy_load')
def test_uninstall(mock_load, mock_un):
    with invoke(main.dip_uninstall, ['fizz']) as result:
        assert result.exit_code == 0
        mock_un.assert_called_once_with('fizz')
