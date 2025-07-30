"""Parses and executes observing sequences in files.
"""

import os
import shutil
import time
import ast
import warnings
import ichigo.scripting.pyscripts as pyscripts

from typing import Callable
from functools import partial
from inspect import getmembers, isfunction
from ichigo.servers import Server
from ichigo.strmanip import simplest_type, print_color, print_line
from ichigo.config import SETTINGS

class ObservingSequence:
    """Parses observing scripts by converting strings into a series of Python
    functions. The Python functions are stored as partials which can then be
    executed later.
    """
    def __init__(self, path: str, servers_dict: dict[str, Server]) -> None:
        """Initializes the ObservingSequence object.

        Parameters
        ----------
        path: str
            Path to the file containing the observing script.
        servers_dict: dict of asmtools.servers.network.Server or a child of this class
            Defines a mapping between aliases and Server object. For example,
            {"rtc": instance of ImakaRTCServer}
        Returns
        -------
        None
        """
        self.path = path
        self.script_name = os.path.basename(path)
        self.servers_dict = servers_dict
        self.funcs_to_exec: list[partial] = []

        self.py_dispatcher: dict[str, Callable] = {
            "print": print,
            "sleep": time.sleep,
            "print_color": print_color,
            "print_line": print_line
        }
        # Import every function in pyscripts
        self.py_dispatcher.update(get_py_scripts())

        # Store special arguments
        self.args_to_convert: dict = {
            "SERVERS": self.servers_dict
        }

    def parse_script(self) -> None:
        """Parses the TXT file defined in self.path and updates the attribute
        self.funcs_to_exec with a list of partial functions.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        print("Parsing script: " + self.script_name)
        # Read the script line by line, storing each function to execute in a list
        funcs_to_exec = []
        with open(self.path, 'r') as f:
            for line in f:
                # Strip off any leading or tailing white spaces
                line = line.strip()
                # Ignore lines that are empty or begin with a '#' symbol
                if len(line) > 0 and line[0] != '#':
                    funcs_to_exec.append(self.parse_line(line))
        # Update self.funcs_to_exec at the end. This ensures that all lines were
        # parsed correctly (no exceptions were raised).
        self.funcs_to_exec = funcs_to_exec
    
    def parse_line(self, line: str) -> partial:
        """Returns a partial function based on the contents of the line.

        Parameters
        ----------
        line: str
            Line to parse.
        
        Returns
        -------
        out: functools.partial
            A partial function that can be stored and executed later.
        """
        line = line.strip()

        # User is executing a server method or standalone function
        if line[0] == '[':
            # Get the name within the brackets, and the rest of the line which
            # should contain the command
            alias, cmd = line[1:].split(']', 1)
            cmd = cmd.strip()
            server = None

            if alias in self.servers_dict:
                # Get the server so we can use its methods
                server = self.servers_dict[alias]

                # Check if it's is a shell command
                if cmd.startswith('$'):
                    cmd = cmd[1:].strip()
                    return partial(server.execute, cmd)
                elif cmd.startswith('!$'):
                    cmd = cmd[2:].strip()
                    return partial(server.execute_fast, cmd)
            elif alias != "py":
                raise ValueError("Failed to resolve the server name in: " + line)
                
            # Parse the function and its arguments
            tree = ast.parse(cmd)
            funccall = tree.body[0].value
            func_name = funccall.func.id
            args = [simplest_type(arg) for arg in funccall.args]
            kwargs = {arg.arg: simplest_type(arg.value) for arg in funccall.keywords}

            # Replace special arguments beginning with _
            args = [self.convert_argument(a[1:]) if isinstance(a, str) and a[0] == "_"
                    else a for a in args]
            kwargs = {k: self.convert_argument(v[1:]) if isinstance(v, str) and v[0] == "_"
                      else v for k, v in kwargs.items()}
            
            if server:
                try: f = server.methods_dict[func_name]
                except:
                    raise ValueError(func_name + " is not a known method of " + type(server).__name__)

            else:
                try: f = self.get_py_func(func_name)
                except KeyError:
                    raise ValueError(func_name + " is not a known function in pyscripts")
                
            return partial(f, *args, **kwargs)
            
        # User is defining a variable
        elif line[0] == '_':
            # Separate the variable name from the value
            var_name, value = line[1:].split("=", 1)
            var_name = var_name.strip()
            value = value.strip()
            # "!SERVERS" is reserved to pass servers_dict as a function parameter
            if var_name == "SERVERS":
                raise ValueError("_SERVERS cannot be redefined. Error in: " + line)
            value = simplest_type(value)
            # Update the list of special arguments
            self.args_to_convert.update({var_name: value})
            do_nothing = lambda: None
            return partial(do_nothing)
        raise ValueError("Failed to recognize starting character in: " + line)
    
    def execute_script(self) -> list:
        """Executes the script. The functions to execute should be defined, in
        order, in self.funcs_to_exec.

        Parameters
        ----------
        None

        Returns
        -------
        out: list
            List of returned values for each executed function.
        """
        if len(self.funcs_to_exec) > 0:
            print("Executing script: " + self.script_name)
            # Iterate through the list and execute one function at a time
            results = []
            results = [f() for f in self.funcs_to_exec]
            print("Values returned by script: ")
            for r in results:
                print(f"  {repr(r)}")
            return results
        
        raise ValueError("No functions to execute in " + self.script_name \
                        + "\n Please check that the script was parsed correctly.")

    def get_py_func(self, func_name: str) -> Callable:
        """Returns a Python function exposed in the dispatcher.
        """
        return self.py_dispatcher[func_name]

    def convert_argument(self, arg: str) -> str:
        """Returns a converted script argument.
        """
        # Return the converted argument if specified in args_dict
        # Otherwise, return the original argument
        if arg in self.args_to_convert:
            return self.args_to_convert[arg]
        return arg
    

def add_script(fname: str, overwrite: bool = False) -> None:
    """Adds a script to the available observing scripts.

    Parameters
    ----------
    fname: str
        Path to the observing script to add.
    overwrite: bool, optional
        If True, overwrite an existing observing script with the same base name
        as fname.

    Returns
    -------
    None
    """
    assert fname.lower().endswith(".txt"), "Script must be a stored in a TXT file"
    assert os.path.isfile(fname), "File must exist"

    # Get directory where scripts are stored
    script_abspath = SETTINGS["PATHS"]["txtscripts"]
    # Get the name of the file, check to see if a file of the same name already
    # exists in the observing scripts directory
    name = os.path.basename(fname)
    fname_script_path = os.path.join(script_abspath, name)
    if os.path.isfile(fname_script_path) and not overwrite:
        warnings.warn("Aborting. There already a script with the name " + name + "." \
                      + "Set overwrite to True if you want to replace the existing script")
        return
    # Copy this file to the directory where observing scripts are stored
    shutil.copy(fname, fname_script_path)
    print("Added to available observing scripts: " + fname)


def remove_script():
    """Removes a script form the observing scripts directory.
    """
    pass


def get_script_abspath(name: str) -> str:
    """Returns the absolute path of a script.

    Parameters
    ----------
    name: str
        The base name of the script.

    Returns
    -------
    out: str
        Absolute path to the script.
    """
    script_abspath = SETTINGS["PATHS"]["txtscripts"]
    return os.path.join(script_abspath, name)


def get_py_scripts() -> dict[str, Callable]:
    """Returns available python scripts. This function finds all of the functions
    in the module pyscripts that do not begin with a '_'.

    Parameters
    ----------
    None
    
    Returns
    -------
    out: dict
        The function names and functions: {func_name: func, ...}.
    """
    all_funcs = getmembers(pyscripts, isfunction)
    filtered = {}
    for name, func in all_funcs:
        if name[0] != '_':
            filtered[name] = func
    return filtered