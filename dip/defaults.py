"""
Default values.
"""
from . import __version__
from . import utils

PATH = u'/usr/local/bin'
HOME = utils.abspath(__package__, 'config.json')
TEMPLATE = utils.abspath(__package__, 'template.sh')
CONFIG = {u'dips': {},
          u'home': HOME,
          u'path': PATH,
          u'version': __version__}
