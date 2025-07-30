import pkg_resources

version = pkg_resources.get_distribution('jsw-pillow').version
__version__ = version

# pillow modules
from jsw_pillow.modules.watermark import Watermark
from jsw_pillow.modules.std_source import std_source
from jsw_pillow.modules.thumbnail import Thumbnail
