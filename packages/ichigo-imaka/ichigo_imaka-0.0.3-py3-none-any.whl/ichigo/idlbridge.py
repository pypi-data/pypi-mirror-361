"""Helper functions for interacting with IDL.
"""

import os

from astropy.io import fits
from ichigo.config import SETTINGS

# If the Python to IDL bridge is enabled...
if SETTINGS["IDL"]["enable_idl"]:
    import sys
    sys.path.append(SETTINGS["IDL"]["idl_bridge_path"])
    from idlpy import *


def get_IDL(reset_session: bool = True):
    """Returns a Python object that can be used to interact with IDL. If the
    Python to IDL bridge is not enabled in settings.ini, this will throw an error.

    Parameters
    ----------
    reset_session: bool, optional
        If True, runs the ".RESET_SESSION" command to reset the IDL session.

    Returns
    -------
    out: idlpy.IDL
        Python object used to interact with IDL.
    """
    # If IDL is not enabled, prevent execution of this function
    if not SETTINGS["IDL"]["enable_idl"]:
        raise RuntimeError("Python to IDL bridge is not enabled.")
    
    # Reset the IDL session
    if reset_session:
        IDL.run(".RESET_SESSION")

    # This object is imported from idlpy. Change cwd to temporary data folder
    # in an IDL function/procedure wants to save data
    path_temp = SETTINGS["PATHS"]["temp"]
    IDL.run("CD, \'" + path_temp + "\'")
    # Run the startup script to compile functions and routines - must remove .pro
    # from the file name
    startup = os.path.splitext(SETTINGS["IDL"]["idl_startup_path"])[0]
    IDL.run("@" + startup)  # execute line by line

    return IDL


def convert_IDL_kwargs(**kwargs) -> str:
    """Converts keyworded IDL arguments to a cmd str. See examples below.

    Parameters
    ----------
    **kwargs: parameters for IDL method or procedure
        Keywords can be passed as such: keyword="/keyword". This will pass the
        argument as: idl_func(/keyword, ...).

    Returns
    -------
    out: str
        Converted arguments.

    Examples
    --------
    >>> convert_IDL_kwargs(num=3, fname="myfile", open=/open)
    "num=3, fname=\'myfile\', /open"
    >>> convert_IDL_kwargs()
    ""
    >>> convert_IDL_kwargs(num=3)
    "num=3"
    """
    args = ""
    for key, value in kwargs.items():
        # Pass as a keyword
        if value == "/" + key:
            args += value
        # Pass as a normal argument
        else:
            # Insert quotation marks if value is a str
            if isinstance(value, str):
                value = "\'" + value + "\'"
            args += key + "=" + str(value)
        args += ", "
    # Remove last comma. If args is empty, this doesn't do anything
    args = args[:-2]
    return args


def transpose_matrix(fname: str, ext: int = 0, ignore_flag: bool = False) -> None:
    """Transposes the data in a FITS file and overwrites the FITS file. This is
    useful for converting matrices generated in IDL.

    Parameters
    -----------
    fname: str
        Path to FITS file to open.
    ext: int, optional
        Extension of the data.
    ignore_flat: bool, optional
        If True, ignores the

    Returns
    -------
    None
    """
    # Set the name of the flag - this will be used to check whether this function
    # has already been used on the file
    flag = "ATRNSPED"
    # Open the HDU list and retrieve the specified extension
    hdu_list = fits.open(fname)
    hdu = hdu_list[ext]
    # Check the header to see if the flag exists
    header = hdu.header
    if flag in header:
        # If it exists and ignore_flag is toggled, set to False
        if ignore_flag:
            header.remove(flag)
        else:
            raise OSError("transpose_matrix has already been performed on " + fname \
                          + "\nSet ignore_flag = True if you want to redo this operation anyway.")
    else:
        header[flag] = "True"
    hdu.header = header
    # Transpose the data
    hdu.data = hdu.data.T
    # Overwrite the file
    hdu_list[ext] = hdu
    hdu_list.writeto(fname, overwrite=True)