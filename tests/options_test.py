import os

import click
import mock
import pytest
from dip import options


def test_validate_all_or_name():
    mock_ctx = mock.MagicMock()
    mock_ctx.params = {'all_opt': True}
    with pytest.raises(click.BadOptionUsage):
        options.validate_all_or_name(mock_ctx, mock.MagicMock(), 'fizz')


def test_validate_env():
    ret = options.validate_env(mock.MagicMock(),
                               mock.MagicMock(),
                               ('FIZZ=BUZZ', 'FUZZ=JAZZ', 'HOME'))
    exp = {'FIZZ': 'BUZZ', 'FUZZ': 'JAZZ', 'HOME': os.getenv('HOME')}
    assert ret == exp


def test_validate_env_err():
    with pytest.raises(click.BadParameter):
        options.validate_env(mock.MagicMock(),
                             mock.MagicMock(),
                             ('FIZZ:BUZZ',))


def test_validate_secret_err():
    with pytest.raises(click.BadParameter):
        options.validate_secret(mock.MagicMock(),
                                mock.MagicMock(),
                                ('test',))
