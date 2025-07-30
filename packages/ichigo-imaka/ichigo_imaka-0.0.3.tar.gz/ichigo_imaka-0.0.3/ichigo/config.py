"""Imports settings.ini as an object with enforced data types. Stores the parameters
in the variable SETTINGS that can be imported into other modules.

This has similar functionality to configobj but permits extended interpolation
in the INI files.
"""

import os
import configparser as cp
import numpy as np
from typing import Any

from ichigo.strmanip import simplest_type


def check_dtype(value: str, dtype: str) -> tuple[bool, Any]:
    """Checks if the value can be converted to the specified data type.

    Parameters
    ----------
    value: str
        Value to check.
    dtype: str
        Data type to check against.
    
    Returns
    -------
    out1: bool
        True if the value can be converted to the data type.
    out2: Any
        Value converted to an instance of a Python type.
    """
    # Parameters can always be taken as strings
    if dtype == "str":
        return True, str(value)
    
    # Get the simplest type of the value
    typed_value = simplest_type(value)
    dtype_found = type(typed_value).__name__

    # Allow integers to be converted to floats
    if dtype == "float" and dtype_found == "int":
        return True, float(typed_value)
    
    return dtype == dtype_found, typed_value


def import_settings(fn_settings: str, fn_dtypes: str) -> dict[str, dict[str, Any]]:
    """Imports settings from settings.ini with types validated from settings.types.ini.

    Parameters
    ----------
    fn_settings: str, optional
        Name of file with parameters.
    fn_dtypes: str, optional
        Name of file with parameters' types.
    
    Returns
    -------
    out: dict
        Dictionary with the settings.
    """
    settings_dict = {}

    settings = cp.ConfigParser(inline_comment_prefixes='#',
                                 interpolation=cp.ExtendedInterpolation()
                                 )
    dtypes = cp.ConfigParser(inline_comment_prefixes='#',
                                interpolation=cp.ExtendedInterpolation()
                                )
    # Allow for case-sensitive parameter names
    settings.optionxform = str
    dtypes.optionxform = str

    settings.read(fn_settings)
    dtypes.read(fn_dtypes)

    # Sections must match, order doesn't matter
    sections = settings.sections()
    assert set(dtypes.sections()) == set(sections), "Sections in settings.ini and" \
        + " settings.types.ini must match."

    for section in sections:
        # Parameters in each section must match
        settings_keys = [x[0] for x in settings.items(section)]
        dtypes_keys = [x[0] for x in dtypes.items(section)]
        
        assert set(settings_keys) == set(dtypes_keys), f"Items in {section} must match" \
            + " in settings.ini and settings.types.ini."
        
        settings_dict[section] = {}

        # Check the type of every item before adding to the settings_dict
        for key, value in settings.items(section):
            dtype = dtypes[section][key]
            result, typed_value = check_dtype(value, dtype)
            assert result, f"Expected {dtype} for {key} in {section}," \
                + f" but got " + str(type(typed_value))
            
            settings_dict[section][key] = simplest_type(value)

    return settings_dict


def make_settings(fn_settings: str | None = None)-> dict[str, dict[str, Any]]:
    """Creates the SETTINGS dictionary from settings.ini.

    Parameters
    ----------
    fn_settings: str, optional
        Path to settings.ini. If None, uses the default settings.ini in the same
        directory as this module.
    fn_dtypes: str, optional
        Path to settings.types.ini. If None, uses the default settings.types.ini
        in the same directory as this module.

    Returns
    -------
    out: dict
        Dictionary with the settings.
    """
    # Get default settings files
    file_path = os.path.abspath(os.path.dirname(__file__))
    if fn_settings is None:
        fn_settings = os.path.join(file_path, "settings.ini")
    
    fn_dtypes =   os.path.join(file_path, "settings.types.ini")
    settings_dict = import_settings(fn_settings, fn_dtypes)

    # Set additional parameters based on the imported parameters below...

    # Lambda f / D in pixels on the image plane
    F = settings_dict["IMAGING"]["F_ratio"]
    wl = settings_dict["IMAGING"]["wavelength"]
    ps = settings_dict["IMAGING"]["pixel_size"]
    settings_dict["IMAGING"]["resolution_element"] = F * wl / ps

    # Conversion matrices for tip-tilt and RA, Dec
    theta = settings_dict["AO"]["ra_dec_theta"] * np.pi/180
    s2 = settings_dict["AO"]["ra_dec_s2"]
    s3 = settings_dict["AO"]["ra_dec_s3"]
    # Take the dot product of this matrix with the Noll Zernike coefficients [a2, a3]
    # in RMS surface to get [RA, Dec] offset in arcseconds.
    settings_dict["AO"]["NollSurface_to_RADec"] = np.array(
        [[s2*np.cos(theta), s3*np.sin(theta)],
         [-1*s2*np.sin(theta), s3*np.cos(theta)]]
    ) * 180/np.pi * 3600 / (settings_dict["AO"]["D_dm"] * 1e3)
    # Invert the matrix for the opposite conversion
    settings_dict["AO"]["RADec_to_NollSurface"] = np.linalg.inv(
        settings_dict["AO"]["NollSurface_to_RADec"]
        )

    return settings_dict

SETTINGS = make_settings()