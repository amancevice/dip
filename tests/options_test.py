import os

import click
import mock
import pytest
from dip import options


def test_validate_env():
    ret = options.validate_env(mock.Mock(), mock.Mock(),
                               ('FIZZ=BUZZ', 'FUZZ=JAZZ', 'HOME'))
    exp = {'FIZZ': 'BUZZ', 'FUZZ': 'JAZZ', 'HOME': os.getenv('HOME')}
    assert ret == exp


def test_validate_env_err():
    with pytest.raises(click.BadParameter):
        options.validate_env(mock.Mock(), mock.Mock(), ('FIZZ:BUZZ',))


def test_validate_secret_err():
    with pytest.raises(click.BadParameter):
        options.validate_secret(mock.Mock(), mock.Mock(), ('test',))


def test_split_remote():
    ret = options.split_remote(mock.Mock(), mock.Mock(), 'origin/master')
    assert ret == ('origin', 'master')


def test_split_remote_no_branch():
    ret = options.split_remote(mock.Mock(), mock.Mock(), 'origin')
    assert ret == ('origin', None)


def test_split_remote_nones():
    ret = options.split_remote(mock.Mock(), mock.Mock(), None)
    assert ret == (None, None)


def test_expand_home():
    assert options.expand_home(None, None, None) is None


def test_ensure_remote():
    ctx = mock.MagicMock()
    ctx.params = {'remote': (None, None)}
    with pytest.raises(click.BadParameter):
        options.ensure_remote(ctx, None, True)
