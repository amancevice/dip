import json
import pkg_resources as pkg
import tempfile

import mock
from dip import config
from dip import templates


@mock.patch('pkg_resources.resource_filename')
def test_config_path(mock_filename):
    package = pkg.Requirement.parse('dip')
    config.config_path()
    mock_filename.assert_called_once_with(package, 'config.json')


def test_write_config():
    cfg = {'dips': [], 'path': '/fizz/buzz'}
    with tempfile.NamedTemporaryFile() as tmp:
        config.write_config(tmp.name,
                            json.dumps(cfg, sort_keys=True, indent=4))
        tmp.flush()

        ret = tmp.read()
        exp = json.dumps(cfg, sort_keys=True, indent=4).encode('utf-8')
        assert ret == exp


def test_read_default():
    ret = config.read()
    exp = json.loads(templates.config())
    assert ret == exp


def test_read():
    cfg = {'dips': [], 'path': '/fizz/buzz'}
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(json.dumps(cfg, sort_keys=True, indent=4).encode('utf-8'))
        tmp.flush()

        ret = config.read(tmp.name)
        assert ret == cfg
