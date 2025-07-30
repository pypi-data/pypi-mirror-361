"""Creates a server object based on the information provided in hosts.json.
"""

import sys

# Import all server types
from ichigo.servers.server import *
from ichigo.servers.imakartc import ImakaRTCServer
from ichigo.servers.ehu import EhuServer
from ichigo.servers.windows import WindowsNUCServer
from ichigo.servers.telescope import TelescopeServer
from ichigo.servers.felixhelper import FELIXHelperServer

def create_server(alias: str) -> Server:
    """Initializes and returns a server object or child class based on information
    in hosts.json.

    Parameters
    ----------
    alias: str
        Alias for the server to create. This is the key in the hosts.json file

    Returns
    -------
    server: ichigo.servers.server.Server or child class
        Initialized server object.
    """
    assert alias != "py", "Cannot use the alias \"py\" to identify a server. \
            This is reserved for executing Python functions."
    
    hosts = import_hosts_dict()
    # Set the Server object type by converting a string to a Python class.
    # This works as long as all of the server classes have been imported
    # above, and is preferable to eval() which allows for arbitrary code
    # execution
    server_type = getattr(sys.modules[__name__], hosts[alias]["type"])
    # Initialize the Server (or child type) object
    host_name = hosts[alias]["host_name"]
    jumps = hosts[alias]["jumps"]
    server = server_type(alias, host_name=host_name, jumps=jumps)
    return server