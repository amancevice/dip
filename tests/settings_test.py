import json
import os
import sys
import tempfile

import compose.project
import git
import mock
import pytest
from dip import errors
from dip import settings
from . import MockSettings

settings.HOME = os.path.expanduser('~/.dip')


@mock.patch('dip.settings.Settings.load')
@mock.patch('dip.settings.Settings.save')
def test_load(mock_save, mock_load):
    with settings.load('/path/to/settings.json'):
        mock_load.assert_called_once_with('/path/to/settings.json')
        mock_save.assert_not_called()


@mock.patch('os.chdir')
@mock.patch('os.path.abspath')
def test_indir(mock_abs, mock_chdir):
    path = os.path.split(__file__)[0]
    mock_abs.return_value = path
    with settings.indir('/tmp/dir'):
        mock_chdir.assert_called_once_with('/tmp/dir')
    mock_chdir.assert_called_with(path)


@mock.patch('dip.settings.load')
@mock.patch('dip.settings.Settings.save')
def test_saveonexit(mock_save, mock_load):
    mock_load.return_value.__enter__.return_value = MockSettings()
    with settings.saveonexit():
        mock_save.assert_not_called()
    mock_save.assert_called_once_with()


@mock.patch('dip.settings.load')
def test_getapp(mock_load):
    with mock.patch('dip.settings.Dip.validate'):
        mock_load.return_value.__enter__.return_value = MockSettings()
        with settings.getapp('fizz') as app:
            assert dict(app) == MockSettings()['fizz']


@mock.patch('dip.settings.load')
def test_getapp_err(mock_load):
    with mock.patch('dip.settings.Dip.validate'):
        mock_load.return_value.__enter__.return_value = MockSettings()
        with pytest.raises(errors.NotInstalledError):
            with settings.getapp('keyerr'):
                pass


@mock.patch('os.remove')
def test_reset(mock_rm):
    settings.reset('/path/to/settings.json')
    mock_rm.assert_called_once_with('/path/to/settings.json')


@mock.patch('os.remove')
def test_reset_err(mock_rm):
    mock_rm.side_effect = OSError
    with pytest.raises(errors.SettingsError):
        settings.reset('/path/to/settings.json')


def test_repo_init():
    with mock.patch('git.Repo'):
        repo = settings.Repo('./fizz/buzz')
        assert repo.path == os.path.abspath('./fizz/buzz')


def test_repo_str():
    repo = settings.Repo('.')
    assert str(repo) == os.path.abspath('.')


def test_repo_repr():
    repo = settings.Repo('.')
    assert repr(repo) == "Repo({})".format(os.path.abspath('.'))


@pytest.mark.parametrize(
    'args, expected',
    [(('/tmp/fizzbuzz',), {}),
     (('/tmp/fizzbuzz', 'remote'), {'remote': 'remote'}),
     (('/tmp/fizzbuzz', 'remote', 'branch'), {'remote': 'remote',
                                              'branch': 'branch'}),
     (('/tmp/fizzbuzz', 'remote', 'branch', 5), {'remote': 'remote',
                                                 'branch': 'branch',
                                                 'sleep': 5})])
def test_repo_iter(args, expected):
    with mock.patch('git.Repo'):
        repo = settings.Repo(*args)
        assert dict(repo) == expected


@mock.patch('dip.settings.Repo.repo')
def test_repo_remote(mock_repo):
    repo = settings.Repo('.', 'origin', 'master', 10)
    assert repo.remote
    mock_repo.remote.assert_called_once_with('origin')


@mock.patch('dip.settings.Repo.repo')
def test_repo_remote_none(mock_repo):
    repo = settings.Repo('.')
    assert repo.remote
    mock_repo.remote.assert_called_once_with(None)


def test_repo_branch():
    repo = settings.Repo('.', 'origin', 'branch')
    ret = repo.branch
    assert ret == 'branch'


@mock.patch('git.Repo.active_branch')
def test_repo_branch_active(mock_branch):
    mock_branch.name = 'branch'
    repo = settings.Repo('.', 'origin')
    ret = repo.branch
    assert ret == 'branch'


def test_repo_sleeptime():
    repo = settings.Repo('.', 'origin')
    assert repo.sleeptime == 0


@mock.patch('time.sleep')
def test_repo_sleep(mock_sleep):
    repo = settings.Repo('.', 'origin', sleep=5)
    repo.sleep()
    mock_sleep.assert_called_once_with(5)


@mock.patch('dip.settings.Repo.repo')
@mock.patch('compose.config.config.get_default_config_files')
@mock.patch('subprocess.call')
def test_repo_diffs(mock_call, mock_compose, mock_repo):
    with mock.patch('dip.settings.indir'):
        mock_repo.remote.return_value.name = 'origin'
        mock_compose.return_value = ['/path/to/docker-compose.yml']
        mock_call.return_value = 1
        repo = settings.Repo('.', 'origin', 'master')
        ret = any(repo.diffs())
        mock_repo.remote.return_value.fetch.assert_called_once_with()
        mock_call.assert_called_once_with([
            'git', 'diff', '--exit-code',
            'origin/master:path/to/docker-compose.yml',
            '/path/to/docker-compose.yml'])
        assert ret is True


@mock.patch('dip.settings.Repo.repo')
@mock.patch('compose.config.config.get_default_config_files')
@mock.patch('subprocess.call')
@mock.patch('dip.settings.devnull')
def test_repo_diffs_quiet(mock_null, mock_call, mock_compose, mock_repo):
    with mock.patch('dip.settings.indir'):
        mock_repo.remote.return_value.name = 'origin'
        mock_compose.return_value = ['/path/to/docker-compose.yml']
        mock_call.return_value = 1
        repo = settings.Repo('.', 'origin', 'master')
        ret = any(repo.diffs(quiet=True))
        mock_repo.remote.return_value.fetch.assert_called_once_with()
        mock_call.assert_called_once_with([
            'git', 'diff', '--exit-code',
            'origin/master:path/to/docker-compose.yml',
            '/path/to/docker-compose.yml'],
            stdout=mock_null.return_value.__enter__.return_value,
            stderr=mock_null.return_value.__enter__.return_value)
        assert ret is True


@mock.patch('dip.settings.Repo.repo')
def test_repo_diffs_err(mock_repo):
    with mock.patch('compose.config.config.get_default_config_files'):
        with mock.patch('subprocess.call'):
            with mock.patch('dip.settings.indir'):
                mock_repo.remote.side_effect = \
                    git.exc.GitCommandError('test', 'test')
                repo = settings.Repo('.', 'origin', 'master')
                with pytest.raises(errors.GitFetchError):
                    assert any(repo.diffs())


@mock.patch('subprocess.call')
def test_repo_pull(mock_call):
    with mock.patch('dip.settings.indir'):
        repo = settings.Repo('.', 'origin', 'master')
        repo.pull()
        mock_call.assert_called_once_with(['git', 'pull', 'origin', 'master'])


def test_dip_init():
    ret = settings.Dip('dipex', '/path/to/docker/compose/dir')
    assert ret.name == 'dipex'
    assert ret.home == '/path/to/docker/compose/dir'
    assert ret.path == settings.PATH
    assert ret.env == {}
    assert ret.git == {}


def test_dip_init_path():
    ret = settings.Dip('dipex', '/path/to/docker/compose/dir', '/bin')
    assert ret.name == 'dipex'
    assert ret.home == '/path/to/docker/compose/dir'
    assert ret.path == '/bin'
    assert ret.env == {}
    assert ret.git == {}


def test_dip_init_env():
    ret = settings.Dip('dipex', '/path/to/docker/compose/dir',
                       env={'ENV': 'VAL'})
    assert ret.name == 'dipex'
    assert ret.home == '/path/to/docker/compose/dir'
    assert ret.path == settings.PATH
    assert ret.env == {'ENV': 'VAL'}
    assert ret.git == {}


def test_dip_init_git():
    ret = settings.Dip('dipex', '/path/to/docker/compose/dir',
                       git={'remote': 'origin', 'branch': 'master'})
    assert ret.name == 'dipex'
    assert ret.home == '/path/to/docker/compose/dir'
    assert ret.path == settings.PATH
    assert ret.env == {}
    assert ret.git == {'remote': 'origin', 'branch': 'master'}


def test_dip_str():
    ret = settings.Dip('dipex', '/path/to/docker/compose/dir')
    assert str(ret) == 'dipex'


def test_dip_repr():
    ret = settings.Dip('dipex', '/path/to/docker/compose/dir')
    assert repr(ret) == 'dipex[/path/to/docker/compose/dir]'


def test_dip_getitem():
    ret = MockSettings()['fizz']
    assert ret['name'] == MockSettings().data['fizz']['name']


def test_dip_getitem_err():
    ret = MockSettings()['fizz']
    with pytest.raises(KeyError):
        assert ret['fame']


def test_dip_len():
    assert len(MockSettings()['fizz']) == 5
    assert len(MockSettings()['buzz']) == 4
    assert len(MockSettings()['jazz']) == 4


def test_dip_iter():
    with mock.patch('git.Repo'):
        ret = settings.Dip('dipex', '/path/to/docker/compose/dir', '/bin',
                           {'ENV': 'VAL'}, {'remote': 'origin'})
        assert dict(ret) == {'name': 'dipex',
                             'home': '/path/to/docker/compose/dir',
                             'path': '/bin',
                             'env': {'ENV': 'VAL'},
                             'git': {'remote': 'origin'}}


@mock.patch('dip.settings.Repo')
def test_dip_repo(mock_repo):
    app = settings.Dip('dipex', '/path/to/docker/compose/dir', '/bin',
                       git={'remote': 'origin',
                            'branch': 'master',
                            'sleep': 5})
    assert app.repo
    mock_repo.assert_called_once_with('/path/to/docker/compose/dir',
                                      'origin', 'master', 5)


@mock.patch('compose.cli.command.get_project')
def test_dip_project(mock_proj):
    app = settings.Dip('dipex', '/path/to/docker/compose/dir')
    assert app.project
    mock_proj.assert_called_once_with('/path/to/docker/compose/dir')


@mock.patch('compose.cli.command.get_project')
def test_dip_service(mock_proj):
    app = settings.Dip('dipex', '/path/to/docker/compose/dir')
    assert app.service
    mock_proj.return_value.get_service.assert_called_once_with('dipex')


@mock.patch('compose.config.config.get_default_config_files')
def test_dip_definitions(mock_cfg):
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write('fizzbuzz'.encode('utf8'))
        tmp.flush()
        mock_cfg.return_value = [tmp.name]
        path = os.path.split(tmp.name)[0]
        app = settings.Dip('dipex', path)
        ret = list(app.definitions)
        mock_cfg.assert_called_once_with(path)
        assert ret == ['fizzbuzz']


@mock.patch('dip.settings.Repo.diffs')
def test_dip_diff(mock_diffs):
    mock_diffs.return_value = iter([False])
    app = settings.Dip('dipex', '/path/to/docker/compose/dir', '/bin',
                       git={'remote': 'origin',
                            'branch': 'master',
                            'sleep': 5})
    ret = app.diff()
    assert ret is False


def test_dip_install():
    with tempfile.NamedTemporaryFile() as tmp:
        path, name = os.path.split(tmp.name)
        app = settings.Dip(name, '/path/to/docker/compose/dir', path)
        app.install()
        tmp.flush()
        ret = tmp.read().decode('utf8')
        exp = "#!/bin/bash\ndip run {name} -- $@\n".format(name=name)
        assert ret == exp


@mock.patch('dip.utils.notty')
@mock.patch('dip.settings.indir')
@mock.patch('subprocess.call')
def test_dip_run(mock_call, mock_dir, mock_tty):
    mock_tty.return_value = True
    app = settings.Dip('dipex', '/path/to/docker/compose/dir')
    app.run('--help')
    mock_dir.assert_called_once_with('/path/to/docker/compose/dir')
    mock_call.assert_called_once_with(
        ['docker-compose', 'run', '--rm', '-T', 'dipex', '--help'],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr)


@mock.patch('dip.utils.notty')
@mock.patch('dip.settings.indir')
@mock.patch('subprocess.call')
def test_dip_run_tty(mock_call, mock_dir, mock_tty):
    mock_tty.return_value = False
    app = settings.Dip('dipex', '/path/to/docker/compose/dir')
    app.run('--help')
    mock_dir.assert_called_once_with('/path/to/docker/compose/dir')
    mock_call.assert_called_once_with(
        ['docker-compose', 'run', '--rm', 'dipex', '--help'],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr)


@mock.patch('os.remove')
@mock.patch('compose.cli.command.get_project')
def test_dip_uninstall(mock_proj, mock_rm):
    app = settings.Dip('dipex', '/path/to/docker/compose/dir', '/bin')
    app.uninstall()
    mock_rm.assert_called_once_with('/bin/dipex')
    mock_proj.return_value.networks.remove.assert_called_once_with()


@mock.patch('os.remove')
@mock.patch('compose.cli.command.get_project')
def test_dip_uninstall_os_err(mock_proj, mock_rm):
    mock_rm.side_effect = OSError
    app = settings.Dip('dipex', '/path/to/docker/compose/dir', '/bin')
    app.uninstall()
    mock_rm.assert_called_once_with('/bin/dipex')
    mock_proj.return_value.networks.remove.assert_called_once_with()


@mock.patch('os.remove')
@mock.patch('compose.cli.command.get_project')
def test_dip_uninstall_compose_err(mock_proj, mock_rm):
    mock_proj.side_effect = compose.config.errors.ConfigurationError('')
    app = settings.Dip('dipex', '/path/to/docker/compose/dir', '/bin')
    app.uninstall()
    mock_rm.assert_called_once_with('/bin/dipex')


@mock.patch('compose.cli.command.get_project')
def test_dip_val_nss(mock_proj):
    with mock.patch('git.Repo'):
        mock_proj.return_value.get_service.side_effect = \
            compose.project.NoSuchService('test')
        app = settings.Dip('dipex', '/path/to/docker/compose/dir',
                           git={'remote': 'origin'})
        with pytest.raises(errors.NoSuchService):
            app.validate()


@mock.patch('compose.cli.command.get_project')
def test_dip_val_cfnf(mock_proj):
    with mock.patch('git.Repo'):
        mock_proj.side_effect = \
            compose.config.errors.ComposeFileNotFound('test')
        app = settings.Dip('dipex', '/path/to/docker/compose/dir',
                           git={'remote': 'origin'})
        with pytest.raises(errors.ComposeFileNotFound):
            app.validate()


@mock.patch('git.Repo')
def test_dip_val_nsr(mock_repo):
    mock_repo.return_value.remote.side_effect = ValueError
    app = settings.Dip('dipex', '/path/to/docker/compose/dir',
                       git={'remote': 'origin'})
    with pytest.raises(errors.NoSuchRemoteError):
        app.validate()


@mock.patch('git.Repo')
def test_dip_val_igre(mock_repo):
    mock_repo.side_effect = git.exc.InvalidGitRepositoryError
    app = settings.Dip('dipex', '/path/to/docker/compose/dir',
                       git={'remote': 'origin'})
    with pytest.raises(errors.InvalidGitRepositoryError):
        app.validate()


@mock.patch('git.Repo')
def test_dip_val_no_such_path_error(mock_repo):
    mock_repo.side_effect = git.exc.NoSuchPathError
    app = settings.Dip('dipex', '/path/to/docker/compose/dir',
                       git={'remote': 'origin'})
    with pytest.raises(errors.NoSuchPathError):
        app.validate()


def test_settings_str():
    assert str(settings.Settings()) == '~/.dip/settings.json'


def test_settings_repr():
    assert repr(settings.Settings()) == 'Settings(~/.dip/settings.json)'


def test_settings_getitem():
    cfg = MockSettings()
    assert dict(cfg['fizz']) == MockSettings()['fizz']


def test_settings_setitem():
    cfg = MockSettings()
    cfg['fuzz'] = settings.Dip('fuzz', '/path/to/docker/compose/dir')
    assert dict(cfg['fuzz']) == {'name': 'fuzz',
                                 'home': '/path/to/docker/compose/dir',
                                 'path': settings.PATH}


def test_settings_delitem():
    cfg = MockSettings()
    del cfg['fizz']
    with pytest.raises(KeyError):
        assert cfg['fizz']


@mock.patch('dip.settings.Dip.install')
def test_settings_install(mock_install):
    with mock.patch('dip.settings.Settings.save'):
        cfg = settings.Settings()
        cfg.install('fuzz', '/path/to/docker/compose/dir')
        mock_install.assert_called_once_with()


@mock.patch('json.loads')
def test_settings_load(mock_json):
    with tempfile.NamedTemporaryFile() as tmp:
        cfg = MockSettings()
        cfg.load(tmp.name)
        mock_json.assert_called_once_with('')


@mock.patch('json.loads')
def test_settings_load_err(mock_json):
    mock_json.side_effect = ValueError
    with tempfile.NamedTemporaryFile() as tmp:
        cfg = MockSettings()
        with pytest.raises(errors.SettingsError):
            assert cfg.load(tmp.name)


@mock.patch('json.loads')
@mock.patch('dip.settings.Settings.save')
def test_settings_load_oserr(mock_save, mock_json):
    mock_json.side_effect = OSError
    with tempfile.NamedTemporaryFile() as tmp:
        cfg = MockSettings()
        cfg.load(tmp.name)
        mock_save.assert_called_once_with(tmp.name)


def test_settings_save():
    with tempfile.NamedTemporaryFile() as tmp:
        cfg = MockSettings()
        cfg.save(tmp.name)
        tmp.flush()
        assert tmp.read().decode('utf8') == \
            json.dumps(cfg.data, indent=4, sort_keys=True)


@mock.patch('json.dumps')
def test_settings_save_err(mock_json):
    mock_json.side_effect = ValueError
    with tempfile.NamedTemporaryFile() as tmp:
        cfg = MockSettings()
        with pytest.raises(errors.SettingsError):
            assert cfg.save(tmp.name)


@mock.patch('dip.settings.Dip.uninstall')
def test_settings_uninstall(mock_uninstall):
    with mock.patch('dip.settings.Settings.save'):
        cfg = MockSettings()
        cfg.uninstall('fizz')
        mock_uninstall.assert_called_once_with()


def test_dip_auto_upgrade():
    app = settings.Dip('dipex', '/path/to/docker/compose/dir')
    assert app.auto_upgrade is None


def test_dip_sleep():
    app = settings.Dip('dipex', '/path/to/docker/compose/dir')
    assert app.sleep is None


def test_devnull():
    with settings.devnull() as null:
        assert null
