"""Class for managing the servers in a session.
"""

import getpass

from ichigo.servers import Server, import_hosts_dict, create_server

class Manager:
    """Manages server connections.
    """
    def __init__(self) -> None:
        """Initializes the Manager object.
        """
        self.servers_dict: dict[str, Server] = {}

    def import_enabled_hosts(self) -> None:
        """Imports hosts as servers from hosts.json. These are entered in the
        attribute servers_dict.
        """
        hosts = import_hosts_dict()
        # Only import enabled hosts
        for alias in hosts:
            if hosts[alias]["enable"]:
               server = create_server(alias)
               self.add_server(alias, server)
    
    def add_server(self, alias: str, server: Server) -> None:
        """Adds a server to the server dict.

        Parameters
        ----------
        alias: str
            Alias for this server.
        server: ichigo.servers.network.Server or a child of this class
            Server to add.
        """
        alias = alias.strip()
        self.servers_dict[alias] = server
    
    def get_server(self, alias: str) -> Server:
        """Returns a Server instance that has been added to the manager.
        """
        return self.servers_dict[alias]

    def connect_all(self, auth_dict: dict = {}) -> None:
        """Connects to every server in servers_dict.

        Parameters
        ----------
        auth_dict: dict, optional
            Dictionary of usernames and passwords for the connections in the format:
              {name1: {use1r:my_username1, pwd:my_pass1}, name2: ...}
        
        Returns
        -------
        None
        """
        all_servers = import_hosts_dict()
        # Don't ask for credentials for any local servers
        for alias in self.servers_dict:
            # Check if there's a host name defined for each server. If not, then
            # add an empty dictionary to auth_dict so we won't ask for credentials
            if not self.servers_dict[alias].host_name:
                auth_dict[alias] = {}
        
        # Server can ask for credentials by itself if no auth_dict is given.
        # Defining auth_dict here to prevent asking for repeat credentials
        for alias, server in self.servers_dict.items():
            # Keep track of which servers we have connected to so we don't ask
            # for the same credentials more than once
            hosts_for_server = server.jumps + [server.alias]

            for jump_alias in hosts_for_server:
                if jump_alias not in auth_dict:
                    print("Authenticating " + jump_alias)
                    # Check if a username is specified in hosts.json
                    user = all_servers[jump_alias]["user"]
                    host_name = all_servers[jump_alias]["host_name"]
                    if not user:
                        # Username not specified, so ask for it
                        user = input("  user for " + host_name + ": ")
                    pwd = getpass.getpass("  pwd for " + user + "@" + host_name + ": ")
                    auth_dict[jump_alias] = {"user": user, "pwd": pwd}
            # Attempt to connect to the server with the supplied credentials
            server.connect(auth_dict)

    def disconnect_all(self) -> None:
        """Disconnects from every server in the servers_dict.
        """
        for alias, server in self.servers_dict.items():
            server.disconnect()