"""Computes wavefront from donut...
"""

import numpy as np
import matplotlib.pyplot as plt

from astropy.io import fits
from numpy.typing import NDArray
from ichigo.idlbridge import get_IDL, convert_IDL_kwargs
from ichigo.config import SETTINGS


def donut(fn_img: str, fn_par: str | None = None) -> NDArray:
    """Approximates Zernike coefficients from an extrafocal image using the donut
    method.
    Reference: Tokovinin & Heathcote (2006)

    Parameters
    ----------
    fn_img: str
        File name of the image.
    fn_par: str, optional
        Parameter file name. If None, the parameter file defined in settings.ini
        is used.

    Returns
    -------
    out: nd_array
        Zernike coefficients.
    """
    if fn_par is None:
        fn_par = SETTINGS["IDL"]["idl_donut_par"]

    IDL = get_IDL()
    cmd_str = f"result = donut(\'{fn_img}\', pfile=\'{fn_par}\')"
    IDL.run(cmd_str, stdout=True)
    result = np.array(IDL.result)

    return result