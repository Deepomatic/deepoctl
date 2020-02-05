import os
from gevent.monkey import patch_all

if os.getenv('DEEPOMATIC_CLI_GEVENT_MONKEY_PATCH', '1') == '1':
    patch_all(thread=False, time=False)  # NOQA

from .version import __version__

__all__ = ["__version__"]
