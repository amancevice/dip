import contextlib
import json

import click.testing
import docker
import git
import mock
import pytest

import dip
from dip import colors
from dip import errors
from dip import main
from dip import settings
from . import MockSettings


@contextlib.contextmanager
def invoke(command, args=None):
    runner = click.testing.CliRunner()
    yield runner.invoke(command, args or [])


def test_clickerr():
    mock_func = mock.MagicMock()
    mock_func.side_effect = errors.DipError()
    with pytest.raises(click.ClickException):
        main.clickerr(mock_func)()


def test_dip():
    with invoke(main.dip) as result:
        assert result.exit_code == 0


def test_version():
    with invoke(main.dip, ['--version']) as result:
        assert result.exit_code == 0
        assert result.output == \
            "dip, version {vsn}\n".format(vsn=dip.__version__)


@mock.patch('subprocess.Popen.communicate')
def test_completion(mock_comm):
    mock_comm.return_value = (b'Hello, world!', None)
    with invoke(main.dip_completion) as result:
        mock_comm.assert_called_once_with()
        assert result.exit_code == 0
        assert result.output == 'Hello, world!\n'


@mock.patch('dip.settings.load')
@mock.patch('subprocess.call')
@mock.patch('dip.utils.editor')
def test_config_edit(mock_ed, mock_call, mock_load):
    mock_ed.return_value = '/bin/vim'
    mock_load.return_value.__enter__.return_value = MockSettings()
    with invoke(main.dip_config, ['--edit']) as result:
        mock_call.assert_called_once_with(
            ['/bin/vim', '/path/to/settings.json'])


@mock.patch('dip.settings.load')
@mock.patch('subprocess.call')
@mock.patch('dip.utils.editor')
def test_config_edit_err(mock_ed, mock_call, mock_load):
    mock_ed.side_effect = KeyError
    mock_load.return_value.__enter__.return_value = MockSettings()
    with invoke(main.dip_config, ['--edit']) as result:
        mock_call.assert_not_called()


@mock.patch('dip.settings.load')
def test_config_string(mock_load):
    mock_load.return_value.__enter__.return_value = MockSettings()
    with invoke(main.dip_config, ['fizz', 'env', 'FIZZ']) as result:
        assert result.exit_code == 0
        assert result.output == \
            MockSettings()['fizz']['env']['FIZZ'] + '\n'


@mock.patch('dip.settings.load')
def test_config_json(mock_load):
    mock_load.return_value.__enter__.return_value = MockSettings()
    with invoke(main.dip_config, ['fizz']) as result:
        assert result.exit_code == 0
        assert result.output == json.dumps(MockSettings().data['fizz'],
                                           indent=4,
                                           sort_keys=True) + '\n'


@mock.patch('dip.settings.load')
def test_config_err(mock_load):
    mock_load.return_value.__enter__.return_value = MockSettings()
    with invoke(main.dip_config, ['fuzz']) as result:
        assert result.exit_code != 0


@mock.patch('dip.settings.getapp')
@mock.patch('dip.settings.Dip.diff')
def test_diff(mock_diff, mock_getapp):
    mock_app = mock.MagicMock()
    mock_getapp.return_value.__enter__.return_value = mock_app
    with invoke(main.dip_diff, ['fizz', '--quiet']) as result:
        mock_app.diff.assert_called_once_with(True)
        assert result.exit_code == 1
        assert result.output == ''


@mock.patch('dip.settings.saveonexit')
@mock.patch('dip.settings.Settings.install')
def test_install_sleep(mock_ins, mock_load):
    mock_load.return_value.__enter__.return_value = MockSettings()
    with invoke(main.dip_install, ['fizz', '/test/path',
                                   '--env', 'FIZZ=BUZZ',
                                   '--path', '/path/to/bin',
                                   '--remote', 'origin/master',
                                   '--sleep', '5']):
        mock_ins.assert_called_once_with(
            'fizz', '/test/path', '/path/to/bin',
            {'FIZZ': 'BUZZ'},
            {'remote': 'origin',
             'branch': 'master',
             'sleep': 5,
             'auto_upgrade': False})


@mock.patch('dip.settings.saveonexit')
@mock.patch('dip.settings.Settings.install')
def test_install_autoup(mock_ins, mock_load):
    mock_load.return_value.__enter__.return_value = MockSettings()
    with invoke(main.dip_install, ['fizz', '/test/path',
                                   '--env', 'FIZZ=BUZZ',
                                   '--path', '/path/to/bin',
                                   '--remote', 'origin/master',
                                   '--auto-upgrade']):
        mock_ins.assert_called_once_with(
            'fizz', '/test/path', '/path/to/bin',
            {'FIZZ': 'BUZZ'},
            {'remote': 'origin',
             'branch': 'master',
             'sleep': None,
             'auto_upgrade': True})


@mock.patch('dip.settings.saveonexit')
@mock.patch('dip.settings.Settings.install')
def test_install_no_exe(mock_ins, mock_load):
    mock_load.return_value.__enter__.return_value = MockSettings()
    with invoke(main.dip_install, ['fizz', '/test/path',
                                   '--env', 'FIZZ=BUZZ',
                                   '--path', '/path/to/bin',
                                   '--remote', 'origin/master',
                                   '--sleep', '5',
                                   '--no-exe']):
        mock_ins.assert_not_called()


@mock.patch('dip.settings.load')
@mock.patch('git.Repo')
def test_list(mock_repo, mock_load):
    mock_repo.return_value.active_branch.name = 'edge'
    mock_load.return_value.__enter__.return_value = MockSettings()
    with invoke(main.dip_list) as result:
        assert result.exit_code == 0
        assert result.output == '''
buzz /path/to/buzz origin/edge
fizz /path/to/fizz origin/master
jazz /path/to/jazz

'''


@mock.patch('dip.settings.load')
@mock.patch('git.Repo')
def test_list_git_err(mock_repo, mock_load):
    mock_repo.side_effect = git.exc.GitCommandError('test', 'test')
    mock_load.return_value.__enter__.return_value = MockSettings()
    with invoke(main.dip_list) as result:
        assert result.exit_code == 0
        assert result.output == '''
buzz /path/to/buzz [git error]
fizz /path/to/fizz origin/master
jazz /path/to/jazz

'''


@mock.patch('dip.settings.getapp')
def test_pull(mock_load):
    with invoke(main.dip_pull, ['fizz']) as result:
        mock_load.return_value.__enter__\
            .return_value.service.pull.assert_called_once_with()
        assert result.exit_code == 0


@mock.patch('dip.main.warnask')
@mock.patch('dip.settings.diffapp')
def test_pull_ask(mock_diffapp, mock_ask):
    mock_app = mock.MagicMock()
    mock_app.git = {}
    mock_diffapp.return_value.__enter__.return_value = (mock_app, 'DIFF')
    with invoke(main.dip_pull, ['fizz']) as result:
        mock_ask.assert_called_once_with(mock_app)
        mock_app.service.pull.assert_called_once_with()
        assert result.exit_code == 0


@mock.patch('dip.settings.getapp')
def test_pull_err(mock_load):
    mock_load.return_value.__enter__\
        .return_value.service.pull.side_effect = Exception
    with invoke(main.dip_pull, ['fizz']) as result:
        mock_load.return_value.__enter__\
            .return_value.service.pull.assert_called_once_with()
        assert result.exit_code != 0


@mock.patch('dip.settings.getapp')
@mock.patch('dip.settings.Dip.service')
@mock.patch('dip.settings.Dip.diff')
def test_pull_docker_err(mock_diff, mock_svc, mock_app):
    mock_diff.return_value = False
    mock_app.return_value.__enter__.return_value = MockSettings()['fizz']
    mock_svc.pull.side_effect = docker.errors.APIError('test')
    with invoke(main.dip_pull, ['fizz']) as result:
        assert result.exit_code != 0


@mock.patch('dip.settings.reset')
def test_reset(mock_reset):
    with invoke(main.dip_reset, ['--force']) as result:
        assert result.exit_code == 0
        mock_reset.assert_called_once_with()


@mock.patch('os.remove')
def test_reset_err(mock_rm):
    mock_rm.side_effect = OSError
    with invoke(main.dip_reset, ['--force']) as result:
        assert result.exit_code != 0


@mock.patch('dip.main.warnask')
@mock.patch('dip.settings.diffapp')
def test_run_ask(mock_diffapp, mock_ask):
    mock_app = mock.MagicMock()
    mock_app.auto_upgrade = False
    mock_app.sleep = False
    mock_diffapp.return_value.__enter__.return_value = (mock_app, 'DIFF')
    with invoke(main.dip_run, ['fizz', '--',
                               '--opt1', 'val1',
                               '--flag']) as result:
        mock_ask.assert_called_once_with(mock_app)
        mock_app.run.assert_called_once_with('--opt1', 'val1', '--flag')
        assert result.exit_code == 0


@mock.patch('dip.main.warnsleep')
@mock.patch('dip.settings.diffapp')
def test_run_sleep(mock_diffapp, mock_sleep):
    mock_app = mock.MagicMock()
    mock_app.sleep = 10
    mock_diffapp.return_value.__enter__.return_value = (mock_app, 'DIFF')
    with invoke(main.dip_run, ['fizz', '--',
                               '--opt1', 'val1',
                               '--flag']) as result:
        mock_sleep.assert_called_once_with(mock_app)
        mock_app.run.assert_called_once_with('--opt1', 'val1', '--flag')
        assert result.exit_code == 0


@mock.patch('dip.main.warnupgrade')
@mock.patch('dip.settings.diffapp')
def test_run_autoupgrade(mock_diffapp, mock_autoup):
    mock_app = mock.MagicMock()
    mock_app.auto_upgrade = True
    mock_app.sleep = False
    mock_diffapp.return_value.__enter__.return_value = (mock_app, 'DIFF')
    with invoke(main.dip_run, ['fizz', '--',
                               '--opt1', 'val1',
                               '--flag']) as result:
        mock_autoup.assert_called_once_with(mock_app)
        mock_app.run.assert_called_once_with('--opt1', 'val1', '--flag')
        assert result.exit_code == 0


@mock.patch('dip.settings.getapp')
def test_run_quick(mock_getapp):
    mock_app = mock.MagicMock()
    mock_getapp.return_value.__enter__.return_value = mock_app
    with invoke(main.dip_run, ['fizz', '--quick', '--',
                               '--opt1', 'val1',
                               '--flag']) as result:
        mock_app.diff.assert_not_called()
        mock_app.run.assert_called_once_with('--opt1', 'val1', '--flag')
        assert result.exit_code == 0


@mock.patch('dip.settings.getapp')
def test_show(mock_app):
    mock_app.return_value.__enter__.return_value.diff.return_value = False
    mock_app.return_value.__enter__.return_value.definitions = iter(['TEST'])
    with invoke(main.dip_show, ['fizz']) as result:
        assert result.exit_code == 0
        assert result.output == '\nTEST\n\n'


@mock.patch('dip.main.warnask')
@mock.patch('dip.settings.diffapp')
def test_show_ask(mock_diffapp, mock_ask):
    mock_app = mock.MagicMock()
    mock_app.git = {}
    mock_app.definitions = iter(['TEST'])
    mock_diffapp.return_value.__enter__.return_value = (mock_app, 'DIFF')
    with invoke(main.dip_show, ['fizz']) as result:
        mock_ask.assert_called_once_with(mock_app)
        assert result.exit_code == 0
        assert result.output == '\nTEST\n\n'


@mock.patch('dip.settings.getapp')
def test_show_sleep(mock_app):
    mock_app.return_value.__enter__.return_value.name = 'myapp'
    mock_app.return_value.__enter__.return_value.repo.sleeptime = 10
    mock_app.return_value.__enter__.return_value.diff.return_value = True
    mock_app.return_value.__enter__.return_value.definitions = iter(['TEST'])
    with invoke(main.dip_show, ['fizz']) as result:
        assert result.exit_code == 0
        assert result.output == \
            '\nLocal service has diverged from remote or is inaccessible.\n'\
            'Sleeping for 10s\n'\
            'CTRL-C to exit\n\n'\
            'Run `dip upgrade myapp` to git-pull updates from remote\n\n\n'\
            'TEST\n\n'


@mock.patch('dip.settings.Settings.uninstall')
@mock.patch('dip.settings.saveonexit')
def test_uninstall(mock_load, mock_un):
    mock_load.return_value.__enter__.return_value = MockSettings()
    with invoke(main.dip_uninstall, ['fizz']) as result:
        assert result.exit_code == 0
        mock_un.assert_called_once_with('fizz')


@mock.patch('dip.settings.Dip.uninstall')
@mock.patch('dip.settings.saveonexit')
def test_uninstall_err(mock_load, mock_un):
    mock_load.return_value.__enter__.return_value = MockSettings()
    with invoke(main.dip_uninstall, ['fuzz']) as result:
        assert result.exit_code == 0
        mock_un.assert_not_called()


@mock.patch('dip.settings.getapp')
def test_upgrade(mock_get):
    mock_app = mock.MagicMock()
    mock_get.return_value.__enter__.return_value = mock_app
    with invoke(main.dip_upgrade, ['fizz']) as result:
        assert result.exit_code == 0
        mock_app.repo.pull.assert_called_once_with()


@mock.patch('dip.settings.getapp')
def test_upgrade_err(mock_get):
    mock_app = mock.MagicMock()
    mock_app.repo = None
    mock_get.return_value.__enter__.return_value = mock_app
    with invoke(main.dip_upgrade, ['fizz']) as result:
        assert result.exit_code == 0


@mock.patch('click.confirm')
def test_warnask_no(mock_confirm):
    mock_confirm.return_value = False
    mock_app = mock.MagicMock()
    with pytest.raises(SystemExit):
        main.warnask(mock_app)
    mock_confirm.assert_has_calls([
        mock.call(colors.teal('Attempt to upgrade before continuing?')),
        mock.call(colors.teal('Continue without upgrading?'))])
    mock_app.repo.pull.assert_not_called()


@mock.patch('click.confirm')
def test_warnask_yes(mock_confirm):
    mock_confirm.return_value = True
    mock_app = mock.MagicMock()
    main.warnask(mock_app)
    mock_confirm.assert_called_once_with(
        colors.teal('Attempt to upgrade before continuing?'))
    mock_app.repo.pull.assert_called_once_with()


def test_warnupgrade():
    mock_app = mock.MagicMock()
    main.warnupgrade(mock_app)
    mock_app.repo.pull.assert_called_once_with()
