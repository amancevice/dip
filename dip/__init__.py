"""
dip CLI tool.
"""
import pkg_resources

from dip.settings import Dip

try:
    __version__ = pkg_resources.get_distribution(__package__).version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    __version__ = '0.0.0'                   # pragma: no cover
