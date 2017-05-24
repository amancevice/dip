import compose.config
import git
import mock
import pytest
from dip import contexts
from dip import exc
from dip.config import Dip
from . import CONFIG


@mock.patch('dip.config.Dip.service')
def test_verify_service(mock_svc):
    mock_svc.return_value = 'docker-compose'
    contexts.verify_service(Dip('fizz', '/path/to/fizz', '/path/to/bin'))


@mock.patch('compose.cli.command.get_project')
def test_verify_service_no_project(mock_proj):
    mock_proj.side_effect = compose.config.errors.ComposeFileNotFound([])
    with pytest.raises(exc.ComposeFileNotFound):
        contexts.verify_service(Dip('fizz', '/path/to/fizz', '/path/to/bin'))


@mock.patch('dip.config.Dip.project')
def test_verify_service_no_service(mock_proj):
    mock_proj.get_service.side_effect = compose.project.NoSuchService('fizz')
    with pytest.raises(exc.NoSuchService):
        contexts.verify_service(Dip('fizz', '/path/to/fizz', '/path/to/bin'))


def test_lazy_load():
    mock_ctx = mock.MagicMock()
    with contexts.lazy_load(mock_ctx, 'fizz'):
        mock_ctx.obj.__getitem__.assert_called_once_with('fizz')


@mock.patch('dip.config.DipConfig.__getitem__')
def test_lazy_err(mock_get):
    mock_get.side_effect = KeyError
    mock_ctx = mock.MagicMock()
    mock_ctx.obj = CONFIG
    with pytest.raises(exc.NotInstalledError):
        with contexts.lazy_load(mock_ctx, 'fizz'):
            pass


@mock.patch('dip.contexts.lazy_load')
@mock.patch('dip.contexts.verify_service')
@mock.patch('os.chdir')
@mock.patch('dip.config.Dip.repo')
@mock.patch('dip.config.Dip.diff')
def test_load(mock_diff, mock_repo, mock_chd, mock_ver, mock_lazy):
    mock_ctx = mock.MagicMock()
    mock_ctx.obj = CONFIG
    mock_lazy.return_value.__enter__.return_value = CONFIG['fizz']
    with contexts.load(mock_ctx, 'fizz') as dip:
        mock_ver.assert_called_once_with(dip)
        mock_chd.assert_called_once_with('/path/to/fizz')
        assert dict(dip) == dict(CONFIG['fizz'])


@mock.patch('dip.contexts.lazy_load')
@mock.patch('dip.contexts.verify_service')
@mock.patch('os.chdir')
@mock.patch('git.Repo')
@mock.patch('click.echo')
def test_load_bad_git(mock_echo, mock_repo, mock_chd, mock_ver, mock_lazy):
    mock_repo.side_effect = git.exc.InvalidGitRepositoryError
    mock_ctx = mock.MagicMock()
    mock_ctx.obj = CONFIG
    mock_lazy.return_value.__enter__.return_value = CONFIG['fizz']
    with contexts.load(mock_ctx, 'fizz') as dip:
        mock_ver.assert_called_once_with(dip)
        mock_chd.assert_called_once_with('/path/to/fizz')
        mock_echo.assert_called_once_with(
            "\x1b[38;5;3m'fizz' command has a remote but is not a git "
            "repository\x1b[0m", err=True)
        assert dict(dip) == dict(CONFIG['fizz'])


@mock.patch('dip.contexts.verify_service')
def test_preload(mock_svc):
    mock_ctx = mock.MagicMock()
    mock_ctx.obj = CONFIG
    with contexts.preload(mock_ctx,
                          'fizz', '/path/to/fizz', '/path/to/bin') as obj:
        assert obj.config == CONFIG.config
