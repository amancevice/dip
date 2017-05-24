import os

import click
import mock
import pytest
from dip import options


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
