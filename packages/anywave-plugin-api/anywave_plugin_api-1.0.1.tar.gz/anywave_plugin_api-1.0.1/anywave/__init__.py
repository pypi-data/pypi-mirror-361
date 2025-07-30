# import numpy
# unpack variables passed as arguments
# _, plugin_dir, pid, server_port, data_path, script_path = sys.argv

# sys.path.append(plugin_dir)
# this is a pointer to the module object instance itself.
host = '127.0.0.1'
pid: int = -1
port: int = 59000
properties = dict()

from .getdata import get_data
from .getmarkers import get_markers
from .sendmessage import send_message
from .getprops import get_props
from .debug_connect import debug_connect
from .sendmarkers import send_markers
from .core.channel import Channel
from .core.marker import Marker
from .init import init
from .run import run