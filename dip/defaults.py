"""
Default values.
"""
import pkg_resources as pkg
from . import __version__

PATH = u'/usr/local/bin'
HOME = pkg.resource_filename(pkg.Requirement.parse('dip'), u'dip/config.json')
CONFIG = {u'dips': {},
          u'home': HOME,
          u'path': PATH,
          u'version': __version__}
