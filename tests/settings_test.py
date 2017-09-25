import os
import sys
import tempfile

import git
import mock
import pytest
from dip import settings

SETTINGS = {'fizz': {'name': 'fizz',
                     'home': '/path/to/fizz',
                     'path': '/path/to/bin',
                     'env': {'FIZZ': 'BUZZ', 'JAZZ': 'RAZZ'},
                     'git': {'branch': 'master', 'remote': 'origin'}},
            'buzz': {'name': 'buzz',
                     'home': '/path/to/buzz',
                     'path': '/path/to/bin',
                     'git': {'remote': 'origin'}},
            'jazz': {'name': 'jazz',
                     'home': '/path/to/jazz',
                     'path': '/path/to/bin',
                     'env': {'FIZZ': 'BUZZ', 'JAZZ': 'RAZZ'}}}


@mock.patch('easysettings.JSONSettings.load')
@mock.patch('easysettings.JSONSettings.save')
def test_load(mock_save, mock_load):
    with settings.load('/path/to/settings.json') as ret:
        mock_load.assert_called_once_with('/path/to/settings.json')
        mock_save.assert_not_called()


@mock.patch('easysettings.JSONSettings.load')
@mock.patch('easysettings.JSONSettings.save')
def test_load_err(mock_save, mock_load):
    mock_load.side_effect = OSError
    with settings.load() as ret:
        assert ret == settings.Settings()
        mock_save.assert_called_once_with()


@mock.patch('os.chdir')
@mock.patch('os.path.abspath')
def test_indir(mock_abs, mock_chdir):
    path, filename = os.path.split(__file__)
    mock_abs.return_value = path
    with settings.indir('/tmp/dir'):
        mock_chdir.assert_called_once_with('/tmp/dir')
    mock_chdir.assert_called_with(path)


@mock.patch('git.Repo')
def test_Repo_init(mock_repo):
    repo = settings.Repo('./fizz/buzz')
    assert repo.path == os.path.abspath('./fizz/buzz')


def test_Repo_str():
    repo = settings.Repo('.')
    assert str(repo) == os.path.abspath('.')


def test_Repo_repr():
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
def test_Repo_iter(args, expected):
    with mock.patch('git.Repo'):
        repo = settings.Repo(*args)
        assert dict(repo) == expected


@mock.patch('dip.settings.Repo.repo')
def test_Repo_remote(mock_repo):
    repo = settings.Repo('.', 'origin', 'master', 10)
    ret = repo.remote
    mock_repo.remote.assert_called_once_with('origin')


@mock.patch('dip.settings.Repo.repo')
def test_Repo_remote_none(mock_repo):
    repo = settings.Repo('.')
    ret = repo.remote
    mock_repo.remote.assert_called_once_with(None)


def test_Repo_branch():
    repo = settings.Repo('.', 'origin', 'branch')
    ret = repo.branch
    assert ret == 'branch'


@mock.patch('git.Repo.active_branch')
def test_Repo_branch_active(mock_branch):
    mock_branch.name = 'branch'
    repo = settings.Repo('.', 'origin')
    ret = repo.branch
    assert ret == 'branch'


@mock.patch('dip.settings.Repo.repo')
@mock.patch('compose.config.config.get_default_config_files')
@mock.patch('dip.settings.indir')
@mock.patch('subprocess.call')
def test_Repo_diffs(mock_call, mock_indir, mock_compose, mock_repo):
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


def test_Dip_init():
    ret = settings.Dip('dipex', '/path/to/docker/compose/dir')
    assert ret.name == 'dipex'
    assert ret.home == '/path/to/docker/compose/dir'
    assert ret.path == settings.Settings.PATH
    assert ret.env == {}
    assert ret.git == {}


def test_Dip_init_path():
    ret = settings.Dip('dipex', '/path/to/docker/compose/dir', '/bin')
    assert ret.name == 'dipex'
    assert ret.home == '/path/to/docker/compose/dir'
    assert ret.path == '/bin'
    assert ret.env == {}
    assert ret.git == {}


def test_Dip_init_env():
    ret = settings.Dip('dipex', '/path/to/docker/compose/dir',
                       env={'ENV': 'VAL'})
    assert ret.name == 'dipex'
    assert ret.home == '/path/to/docker/compose/dir'
    assert ret.path == settings.Settings.PATH
    assert ret.env == {'ENV': 'VAL'}
    assert ret.git == {}


def test_Dip_init_git():
    ret = settings.Dip('dipex', '/path/to/docker/compose/dir',
                       git={'remote': 'origin', 'branch': 'master'})
    assert ret.name == 'dipex'
    assert ret.home == '/path/to/docker/compose/dir'
    assert ret.path == settings.Settings.PATH
    assert ret.env == {}
    assert ret.git == {'remote': 'origin', 'branch': 'master'}


def test_Dip_str():
    ret = settings.Dip('dipex', '/path/to/docker/compose/dir')
    assert str(ret) == 'dipex'


def test_Dip_repr():
    ret = settings.Dip('dipex', '/path/to/docker/compose/dir')
    assert repr(ret) == 'dipex[/path/to/docker/compose/dir]'


@mock.patch('git.Repo')
def test_Dip_iter(mock_repo):
    ret = settings.Dip('dipex', '/path/to/docker/compose/dir', '/bin',
                       {'ENV': 'VAL'}, {'remote': 'origin'})
    assert dict(ret) == {'name': 'dipex',
                         'home': '/path/to/docker/compose/dir',
                         'path': '/bin',
                         'env': {'ENV': 'VAL'},
                         'git': {'remote': 'origin'}}


@mock.patch('dip.settings.Repo')
def test_Dip_repo(mock_repo):
    app = settings.Dip('dipex', '/path/to/docker/compose/dir', '/bin',
                       git={'remote': 'origin',
                            'branch': 'master',
                            'sleep': 5})
    ret = app.repo
    mock_repo.assert_called_once_with('/path/to/docker/compose/dir',
                                      'origin', 'master', 5)


@mock.patch('compose.cli.command.get_project')
def test_Dip_project(mock_proj):
    app = settings.Dip('dipex', '/path/to/docker/compose/dir')
    ret = app.project
    mock_proj.assert_called_once_with('/path/to/docker/compose/dir')


@mock.patch('compose.cli.command.get_project')
def test_Dip_project(mock_proj):
    app = settings.Dip('dipex', '/path/to/docker/compose/dir')
    ret = app.service
    mock_proj.return_value.get_service.assert_called_once_with('dipex')


@mock.patch('compose.config.config.get_default_config_files')
def test_Dip_definitions(mock_cfg):
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write('fizzbuzz'.encode('utf8'))
        tmp.flush()
        mock_cfg.return_value = [tmp.name]
        path, name = os.path.split(tmp.name)
        app = settings.Dip('dipex', path)
        ret = list(app.definitions)
        mock_cfg.assert_called_once_with(path)
        assert ret == ['fizzbuzz']


@mock.patch('dip.settings.Repo.diffs')
def test_Dip_diff(mock_diffs):
    mock_diffs.return_value = iter([False])
    app = settings.Dip('dipex', '/path/to/docker/compose/dir', '/bin',
                       git={'remote': 'origin',
                            'branch': 'master',
                            'sleep': 5})
    ret = app.diff()
    assert ret is False


def test_Dip_install():
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
def test_Dip_run(mock_call, mock_dir, mock_tty):
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
def test_Dip_run_tty(mock_call, mock_dir, mock_tty):
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
def test_Dip_uninstall(mock_proj, mock_rm):
    app = settings.Dip('dipex', '/path/to/docker/compose/dir', '/bin')
    app.uninstall()
    mock_rm.assert_called_once_with('/bin/dipex')
    mock_proj.return_value.networks.remove.assert_called_once_with()


def test_Settings_str():
    assert str(settings.Settings()) == settings.Settings.HOME


def test_Settings_repr():
    assert repr(settings.Settings()) == \
        "Settings({home})".format(home=settings.Settings.HOME)


def test_Settings_getitem():
    cfg = settings.Settings(**SETTINGS)
    assert dict(cfg['fizz']) == SETTINGS['fizz']


def test_Settings_setitem():
    cfg = settings.Settings(**SETTINGS)
    cfg['fuzz'] = settings.Dip('fuzz', '/path/to/docker/compose/dir')
    assert dict(cfg['fuzz']) == {'name': 'fuzz',
                                 'home': '/path/to/docker/compose/dir',
                                 'path': settings.Settings.PATH}


def test_Settings_delitem():
    cfg = settings.Settings(**SETTINGS)
    del cfg['fizz']
    with pytest.raises(KeyError):
        cfg['fizz']


@mock.patch('dip.settings.Settings.save')
@mock.patch('dip.settings.Dip.install')
def test_Settings_install(mock_install, mock_save):
    cfg = settings.Settings()
    cfg.install('fuzz', '/path/to/docker/compose/dir')
    mock_install.assert_called_once_with()


@mock.patch('dip.settings.Settings.save')
@mock.patch('dip.settings.Dip.uninstall')
def test_Settings_uninstall(mock_uninstall, mock_save):
    cfg = settings.Settings(**SETTINGS)
    cfg.uninstall('fizz')
    mock_uninstall.assert_called_once_with()
