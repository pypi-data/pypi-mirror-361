"""Base class for all server objects. Manages connections to remote servers via
SSH, and sending commands through them to the terminal.
"""

import json
import getpass
import warnings
import subprocess
import paramiko

from ichigo.strmanip import print_color
from ichigo.config import SETTINGS

class Server:
    """Sends commands to and recieves outputs from a remote server via SSH. Also
    transfers files via SCP.
    
    If the address of the remote server is unspecified, then the commands are
    executed locally.
    """
    def __init__(self, alias: str, host_name: str | None = None, os_type: str ='unix',
                  jumps: list[str] = [], source: list[str] = []) -> None:
        """Initializes the Server object.

        Parameters
        ----------
        alias: str
            Alias for the target host.
        host_name: str or None, optional
            Host name or IP address. If None, shell commands are executed locally.
        os_type: str, optional
            Type of operating system, either 'unix' or 'windows'.
        jumps: list of str, optional
            List of host names to perform ssh jumps through.
        source: list of str, optional
            Any files in this list will be sourced whenever a command is executed.

        Returns
        -------
        None
        """
        #if alias in import_hosts_dict():
        #    warnings.warn("Host name for alias " + alias + " is already defined in hosts.json")

        self.alias = alias
        self.host_name = host_name
        self.jumps = jumps
        self.os_type = os_type
        self.source = source

        self.sshclient: paramiko.client.SSHClient | None = None
        self.old_clients: list[paramiko.client.SSHClient] = []
        # Save a dictionary of methods for parsing observing scripts
        self._set_methods_dict()
    
    def is_remote(self) -> bool:
        """Returns True if this is a remote machine, False if local.
        """
        return self.host_name != None

    def _set_methods_dict(self) -> None:
        """Sets the attribute methods_dict to a dictionary of all class methods
        that do not begin with a "_".

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.methods_dict = {name: getattr(self, name) for name in dir(self) \
                              if callable(getattr(self, name)) and not name.startswith('_')}
    
    def _connect_first(self, addr: str, user: str, pwd: str) -> None:
        """Connects from the local machine to a remote server.
        
        Parameters
        ----------
        addr: str
            Host name to connect to.
        user: str
            Username for the host.
        pwd: str
            Password for the host.

        Returns
        -------
        None
        """
        try: 
            self.sshclient = paramiko.client.SSHClient()
            self.sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.sshclient.connect(addr, username=user, password=pwd)
        except paramiko.ssh_exception.AuthenticationException:
            print_color("WARNING: Target host authentication failed for: " + addr \
                           + "\nDisconnecting.", "red")
            self.disconnect()
            raise paramiko.ssh_exception.AuthenticationException("Failed to connect to " + self.alias)

    def _jump_hosts(self, addr: str, user: str, pwd: str) -> None:
        """Jumps from the current host to new host.

        Reference: https://stackoverflow.com/a/36096801/22266720

        Parameters
        ----------
        addr: str
            Desination address to jump to.
        user: str
            Username to login to the destination server.
        pwd: str
            Password to login to the destination server.

        Returns
        -------
        None
        """
        assert isinstance(self.sshclient, paramiko.client.SSHClient), "Must connect \
              to the first host before jumping"

        try:
            transport = self.sshclient.get_transport()
            local_addr = ('0.0.0.0', 22)
            dest_addr = (addr, 22)
            channel = transport.open_channel("direct-tcpip", dest_addr, local_addr)
            # Connect to the new host
            new_sshclient = paramiko.client.SSHClient()
            new_sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            new_sshclient.connect(dest_addr, username=user, password=pwd, sock=channel)
            # Save the old ssh client so we can close it later, and update the current one
            self.old_clients.append(self.sshclient)
            self.sshclient = new_sshclient
        except paramiko.ssh_exception.AuthenticationException:
            print_color("WARNING: Jump host authentication failed for: " + addr \
                           + "\nDisconnecting.", "red")
            self.disconnect()
            raise paramiko.ssh_exception.AuthenticationException("Failed to connect to " + self.alias)
    
    def connect(self, auth_dict: dict | None = None) -> None:
        """Connects to the target server defined by self.alias, including jumps.

        Paramters
        ---------
        auth_dict: dict or None, optional
            Dictionary of usernames and passwords for the connections in the format:
              {name1: {use1r:my_username1, pwd:my_pass1}, name2: ...}
            If None, this object will ask for the user to input credentials.

        Returns
        -------
        None
        """
        # Do nothing if address indicates that commands should be run locally
        if not self.host_name:
            return
        # Otherwise, begin by checking that all of the host names are defined in
        # auth_dict
        all_host_aliases = self.jumps + [self.alias]
        if auth_dict:
            assert all(host in auth_dict for host in all_host_aliases), "Credentials must be defined \
                for all hosts needed to connect to " + self.alias
        # No auth_dict given - ask for credentials manually
        else:
            auth_dict = {}
            for alias in all_host_aliases:
                host_name = get_host_name(alias)
                user = input("  user for " + host_name + ": ")
                pwd = getpass.getpass("  pwd for " + user + "@" + host_name + ": ")
                auth_dict.update({alias: {"user": user, "pwd": pwd}})

        # If there are no jumps, just connect to the destination address directly
        if len(self.jumps) == 0:
            alias = self.alias
            host_name = self.host_name
            self._connect_first(host_name, user=auth_dict[alias]["user"], pwd=auth_dict[alias]["pwd"])
        # Execute jumps
        else:
            # Get the name of the first host to connect to and its corresponding address
            alias = self.jumps[0]
            host_name = get_host_name(alias)
            self._connect_first(host_name, user=auth_dict[alias]["user"], pwd=auth_dict[alias]["pwd"])
            # Perform any additional jumps if necessary
            for alias in self.jumps[1:]:
                host_name = get_host_name(alias)
                self._jump_hosts(host_name, user=auth_dict[alias]["user"], pwd=auth_dict[alias]["pwd"])
            # Perform final jump to the destination address
            alias = self.alias
            host_name = get_host_name(alias)
            self._jump_hosts(host_name, user=auth_dict[alias]["user"], pwd=auth_dict[alias]["pwd"])
        print("Connected to " + self.host_name)

    def disconnect(self) -> None:
        """Closes the remote connection.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Close the connection if the ssh client is connected
        if self.sshclient:
            self.sshclient.close()
            self.sshclient = None
        # Make sure to close jump host connections as well
        for c in self.old_clients:
            c.close()
        self.old_clients = []
        print("Disconnected from " + self.alias)
    
    def _convert_cmd_source(self, cmd: str) -> str:
        """Converts a shell command to source the files in self.source.

        Parameters
        ----------
        cmd: str
            Shell command to convert.

        Returns
        -------
        out: str
            Shell commmand prepended with source [filename];
        """
        if self.os_type == "unix":
            for fname in self.source:
                prefix = "source " + fname + "; "
                return prefix + cmd
        return cmd

    def _convert_cmd_interactive_shell(self, cmd: str) -> str:
        """Returns the command with a prefix to force an interactive shell. The
        command is converted to "/bin/bash -c "<cmd>"".

        Parameters
        ----------
        cmd: str
            Shell command to convert.
        
        Returns
        -------
        out: str
            Shell command with the prefix.
        """
        if self.os_type == 'unix':
            # set -m enables job control
            # /bin/bash -ic forces interactive shell so we can use aliases
            cmd = cmd.strip()
            return f'set -m; bash -ic "{cmd}" ;'
        return cmd

    def execute(self, cmd: str, print_out: bool = True) -> str:
        """Returns the output of an executed command. This function will wait for
        the command to finish, or will wait until the connection to the remote
        server is terminated.
s
        Parameters
        ----------
        cmd: str
            Shell command to execute.
        print_out: bool, optional
            If True, the output will be printed to the terminal.

        Returns
        -------
        out: str
            Output of the command in the terminal, not including error messages
            (this is stdout).
        """
        # Force interactive shell - does nothing for Windows machines
        if self.sshclient:
            cmd = self._convert_cmd_interactive_shell(cmd)
        # Source files to access aliases
        cmd = self._convert_cmd_source(cmd)
        if self.sshclient:
            # Wait until the command has finished executing by calling recv_exit_status(),
            # otherwise trying to retrieve the output files may result in an error
            std, stdout, stderr = self.sshclient.exec_command(cmd, get_pty=True)
            stdout.channel.recv_exit_status()
            # Print the output to the terminal combined with any error messages
            stdout.channel.set_combine_stderr(True)
            result = ''
            for line in stdout.readlines(): result += line

            if print_out:
                print(result)
            return result
        
        else:
            # subprocess.run() will wait for the output unlike subprocess.Popen(),
            # which will run multiple processes at once. However, trying to
            # execute commands before the previous one is finished isn't really
            # an issue when running things locally
            cp = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if print_out:
                print(cp.stdout)
                print(cp.stderr)
            return cp.stdout
    
    def execute_fast(self, cmd: str) -> None:
        """Executes a command on the server. This function will not wait for the
        command to finish.

        Parameters
        ----------
        cmd: str
            The command to execute.
        
        Returns
        -------
        None
        """
        cmd = self._convert_cmd_interactive_shell(cmd)
        cmd = self._convert_cmd_source(cmd)
        if self.sshclient:
            self.sshclient.exec_command(cmd, get_pty=True)
        else:
            subprocess.Popen(cmd, shell=True)
        
    def sftp_put(self, local_path: str, remote_path: str) -> None:
        """Transfers files from the localhost to the remote server.

        Parameters
        ----------
        local_path: str or list of str
            A single path or list of paths to be transferred.
        remote_path: str
            Directory to transfer files to.

        Returns
        -------
        None
        """
        if self.sshclient:
            sftp = self.sshclient.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
        else:
            warnings.warn(self.alias + " is not a remote server. SFTP failed.")

    def sftp_get(self, remote_path: str, local_path: str) -> None:
        """Transfers files and directories from the remote server to the localhost.

        Parameters
        ----------
        remote_path: str or list of str
            A single path or list of paths to be transferred.
        local_path: str
            Directory to transfer files to.

        Returns
        -------
        None

        """
        if self.sshclient:
            sftp = self.sshclient.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
        else:
            warnings.warn(self.alias + " is not a remote server. SFTP failed.")


def import_hosts_dict() -> dict:
    """Returns a dict constructed from hosts.json.

    Parameters
    ----------
    None

    Returns
    -------
    out: dict
        Dictionary of hosts.
    """
    fname = SETTINGS["RESOURCES"]["hosts"]
    with open(fname, 'r') as f:
        hosts = json.load(f)
    return hosts


def get_host_name(alias: str) -> str:
    """Returns the address corresponding to a alias in hosts.json. If the alias
    is not defined in hosts.json, return the input value.

    Parameters
    ----------
    None

    Returns
    -------
    out: str or None
        Address corresponding to the given alias.
    """
    hosts = import_hosts_dict()
    if alias not in hosts:
        return alias
    return hosts[alias]["host_name"]


def add_host(alias: str, host_name: str | None = None, user: str | None = None,
                jumps: list[str] = [], server_type: str = "Server", enable: bool = True,
                overwrite: bool = False):
    """Appends a host to the list of known addresses. This function modifies
    hosts.json.

    Parameters
    ----------
    alias: str
        Alias of the host.
    host_name: str or None, optional
        Address of the host.
    user: str, optional
        Username to login to the host.
    jumps: list of str, optional
        List of host names to perform ssh jumps through.
    server_type: str, optional
        Server type.
    enable: bool, optional
        If True, the server is enabled.
    overwrite: bool, optional
        If True, overwrite the host if the alias is already registered. If False,
        send a warning and do not overwrite the address.
    
    Returns
    -------
    None
    """
    hosts = import_hosts_dict()
    if (alias in hosts and not overwrite):
        raise ValueError("A host is already registered under this alias." \
                      + " Set overwrite=True to overwrite the host.")

    hosts[alias]["host_name"] = host_name
    hosts[alias]["user"] = user
    hosts[alias]["jumps"] = jumps
    hosts[alias]["type"] = server_type
    hosts[alias]["enable"] = enable

    fname = SETTINGS["RESOURCES"]["hosts"]
    with open(fname, 'w') as f:
        json.dump(hosts, f, sort_keys=True, indent=4)


def remove_host(alias):
    """Removes a host from the list of known addresses, if it exists. This function
    modifies hosts.json. If the specified host is not in the address book, this
    function effectively does nothing.

    Parameters
    ----------
    alias: str
        Alias of the host to remove.

    Returns
    -------
    None
    """
    hosts = import_hosts_dict()
    hosts.pop(alias, None)

    fname = SETTINGS["RESOURCES"]["hosts"]
    with open(fname, 'w') as f:
        json.dump(hosts, f, sort_keys=True, indent=4)