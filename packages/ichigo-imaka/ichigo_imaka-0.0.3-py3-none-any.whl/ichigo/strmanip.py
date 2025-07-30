"""Helper functions for printing and manipulating strings.
"""

import os
import glob
import re
import ast

from typing import Any
from datetime import datetime, timezone


def print_color(s: str, c: str) -> None:
    """Prints a colored string.

    Parameters
    ----------
    s: str
        String to print.
    c: str 
        Color of the string. Options: 'red', 'green', 'yellow', 'blue',
        'magenta', 'cyan', 'black', 'white', 'bold', 'underline'

    Returns
    -------
    None
    """
    color_dict = {
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'black': '\033[30m',
        'white': '\033[37m',
        'bold':'\033[1m',
        'underline': '\033[4m'
    }
    assert c in color_dict, "The ANSI escape sequence for c must be defined print_color"

    color_code = color_dict[c]
    end_code = '\033[0m'
    print(f'{color_code}' + s + f'{end_code}')


def print_line(symbol: str = '-') -> None:
    """Prints a horizontal line in the terminal.

    Parameters
    ----------
    symbol: str, optional
        Character to draw the line with.

    Returns
    -------
    None
    """
    term_size = os.get_terminal_size()
    print(symbol * term_size.columns)


def get_timestamp(date_only: bool = False) -> str:
    """Returns a timestamp string of the current UT time. The default format is:

    'YYYYMMDDTHH:MM:SS+00:00'

    where:
        - YYYYMMDD is the date (year, month, day)
        - The letter "T" is inserted as a separator between the date and time
        - HH:MM:SS is the time (hour, minute, second)
        - The string "+00:00" indicates that the time zone is UTC
    For example, the UTC time of May 10, 2024 at 1:14:07 PM would cause this
    function to return '20240510T13:14:07+00:00'.

    If date_only is enabled, then the returned string is "YYYYMMDD".

    Parameters
    ----------
    date_only: bool, optional
        If True, the output only includes the date (YYYYMMDD).

    Returns
    -------
    out: str
        Formatted time string.
    """
    # Get the UTC time as a datetime.datetime object
    utc_time = datetime.now(timezone.utc)
    # Format the datetime object into a string
    if date_only:
        return utc_time.strftime("%Y%m%d")
    return utc_time.strftime("%Y%m%dT%H:%M:%S+00:00")


def split_ignore_quotes(s: str) -> list[str]:
    """Splits a string according to delimiter ';'. This is similar to the built-in
    function str.split(';'), except this function ignores semicolons inside of
    double quotation marks ('\"'). For example:

    >>> mystr = "myfunc; \"Hello; world!;\"; 5; [1,2,3]"
    >>> split_ignore_quotes(mystr)
    ['myfunc', ' \"Hello, world!;\"', ' 5', ' [1', '2', '3]']

    Reference: https://stackoverflow.com/q/2785755/22266720
    
    Parameters
    ----------
    s: str
        String to split.

    Returns
    -------
    out: list of str
        The input string s split by a semicolon.
    """
    pattern = re.compile(r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')
    return pattern.split(s)[1::2]


def split_str_to_literals(s: str) -> list[Any]:
    """Splits a string according to delimiter ';', and then converts each argument
    to a built-in Python type. This function ignores semicolons inside of
    double quotation marks ('\"'). For example:

    Parameters
    ----------
    s: str
        String to split.

    Returns
    -------
    out: list
        The input string s split by a semicolon and converted to built-in Python
        types.

    Examples
    --------
    >>> mystr = "myfunc; \"Hello; world!;\"; 5; [1,2,3]"
    >>> split_str_to_literal(mystr)
    ['myfunc', 'Hello; world!;', 5, [1, 2, 3]]
    """
    res = split_ignore_quotes(s)
    # Convert each argument in the list to the appropriate datatype
    return [simplest_type(arg.strip()) for arg in res]


def simplest_type(s: str | ast.AST) -> Any:
    """Returns a string or node converted into a Python literal. If literal_eval() \
    fails, returns the original string. If the input is an ast.Name node, returns
    the id of the node.
    """
    if isinstance(s, ast.Name):
        return s.id
    try:
        return ast.literal_eval(s)
    except:
        return s
    

def strip_ansi_codes(s: str) -> str:
    """Strips ANSI escape codes from a string.
    """
    return re.sub(r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?', '', s)


def iso_to_utf8(data_dir: str) -> None:
    """Modifies all .txt files in the specified directory to have UTF-8 encoding.
    Assumes that the encoding of the current text files is ISO-8859-1 (as is the
    case with the HASO data).
    
    Parameters
    ----------
    data_dir: str
        Target directory with .txt files to convert.
    """
    assert os.path.isdir(data_dir), "The directory must exist."
    
    cwd = os.getcwd()
    try:
        os.chdir(data_dir)
        fns = glob.glob("*.txt")
        fns = sorted(fns)
        for fn in fns:
            with open(fn, 'r', encoding='ISO-8859-1') as fin:
                file_data = fin.read()
            with open(fn, 'w', encoding='utf8') as fout:
                fout.write(file_data)
    except:
        print("Reseting cwd")
    os.chdir(cwd)
