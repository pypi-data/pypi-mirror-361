"""Functions for manipulating reconstruction matrices (AKA control matrices, or
cmats).
"""

import warnings
import numpy as np
import matplotlib.pyplot as plt

from astropy.io import fits
from scipy.interpolate import RBFInterpolator
from numpy.typing import NDArray
from ichigo.idlbridge import get_IDL, convert_IDL_kwargs
from ichigo.calc.zernikes import noll_zernike_index, zernike_derv, make_gamma_matrices
from ichigo.calc.cacofoni.make_cacofoni import make_cacofoni
from ichigo.config import SETTINGS


def zernike_filter(j: int, gains: NDArray, cmat: NDArray, z2a: NDArray | None = None, a2z: NDArray | None = None,
                  fn_out: str | None = None) -> NDArray:
    """Applies a piston filter to the control matrix.

    Parameters
    ----------
    j: int
        Noll Zernike index (j = 1 is piston)
    cmat: nd_array
        Control matrix.
    z2a: nd_array, optional
        Zernike-to-actuator matrix. If None, it is loaded from settings.ini.
    a2z: nd_array, optional
        Actuator-to-zernike matrix. If None, it is loaded from settings.ini.
    fn_out: str or None, optional
        File name to save the filtered cmat to, including the file extension. If
        None, the file is not saved.

    Returns
    -------
    out: nd_array
        Control matrix with the piston coefficient zeroed out.
    """
    # Noll indexing starts at 1 so convert to array index
    j -= 1

    if not z2a:
        z2a = fits.getdata(SETTINGS["RESOURCES"]["z2a"], ext=0)
    if not a2z:
        a2z = fits.getdata(SETTINGS["RESOURCES"]["a2z"], ext=0)
    
    n_zernikes = a2z.shape[0]
    n_actuators = a2z.shape[1]
    n_channels = cmat.shape[0]
    n_slopes = cmat.shape[1]
    
    if n_actuators != SETTINGS["AO"]["n_actuators"]:
        warnings.warn("Number of actuators in a2z does not match n_actuators in settings.ini")
    if n_channels != SETTINGS["AO"]["n_channels"]:
        warnings.warn("Number of channels in cmat does not match n_channels in settings.ini")
    if n_slopes != 2*SETTINGS["AO"]["n_subaps"]:
        warnings.warn("Number of slopes in cmat does not match 2*n_subaps in settings.ini")

    # Zero out the zernike coefficient
    z0 = np.identity(n_zernikes)
    z0[j, j] = 0
    z2a_f = np.matmul(z2a, z0)

    # apply the zernike filter
    cmat_mode = np.matmul(a2z, cmat[:n_actuators])
    cmat_filtered = np.matmul(z2a_f, cmat_mode)

    # Pad the result back to match the number of channels in the original cmat
    result = np.zeros((n_channels, n_slopes))
    result[:n_actuators, :] = cmat_filtered
    
    if fn_out:
        hdu = fits.PrimaryHDU(result)   # Suz: modified 'cmat_filtered' to 'result', which is padded
        hdu.header["COMMENT"] = "Zernike "+str(j+1)+" filtered cmat." # Suz: modified to save zernike mode n in comment
        hdu.writeto(fn_out, overwrite=True)
        
    return result

def make_cacophony_imat2(fns_aocb: list[str], minfreq: float, maxfreq: float,
                        plot: bool = True, fn_out: str | None = None, **kwargs) -> NDArray:
    """Python implementation of CACOFONI.
    """
    imats = []
    for fn in fns_aocb:
        freq, psdmes, psdmod, filter_mask, imat, laplacian = make_cacofoni(
            telemetry_filepath=fn,
            **kwargs
        )
        imats.append(imat)

    # Average all of the imats to get final imat
    imat = np.average(imats, axis=0)

    if plot:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6,6))
        # Transpose to match Olivier's plot...
        ax.imshow(imat.T, cmap="PiYG", aspect="auto", origin="lower")
        ax.set_title("imat shape: " + str(imat.shape), fontsize=12)
        plt.show()
    
    if fn_out:
        hdu = fits.PrimaryHDU(imat)
        hdu.header["COMMENT"] = "Python-generated CACOFONI interaction matrix."
        hdu.writeto(fn_out, overwrite=True)

    return imat

def make_cacophony_imat(fns_aocb: list[str], minfreq: float, maxfreq: float,
                        plot: bool = True, fn_out: str | None = None, **kwargs) -> NDArray:
    """Makes a CACOFONI interaction matrix from 'imaka aocb files.

    Parameters
    ----------
    fns_aocb: list of str
        List aocb file names.
    minfreq: float
        Minimum frequency.
    maxfreq: float
        Maximum frequency.
    plot: bool, optional
        If True, plots the imat.
    fn_out: str or None, optional
        File name to save imat to, including the file extension. If None, the
        file is not saved.
    **kwargs: parameters to make_cacophony.pro
        Optional parameters for the IDL function make_cacophony. See documentation
        for helpers.idlbridge.convert_IDL_kwargs().
        
    Returns
    -------
    out: nd_array 
        Interaction matrix. Expected shape is (n_actuators, 2*n_subaps), but this
        is currently hard-coded in make_cacophony.pro for IRTF-ASM-1.
    """
    assert minfreq < maxfreq, "minfreq must be less than maxfreq"
    minfreq = float(minfreq)
    maxfreq = float(maxfreq)

    IDL = get_IDL()

    # Create interaction matrices
    imats = []
    for i, fn in enumerate(fns_aocb):
        # Create variable name to assign in idl
        varname = "imat" + str(i)
        cmd_str = varname + "=make_cacophony(" + "\'" + fn + "\', " + str(minfreq) \
            + ", " + str(maxfreq)
        # Pass any other arguments
        if len(kwargs) > 0:
            cmd_str += ", " + convert_IDL_kwargs(**kwargs)
        cmd_str += ")"

        IDL.run(cmd_str, stdout=True)
        # Retrieve the variable as a numpy array and store it
        imats.append(eval("IDL." + varname))
        
    # Average all of the imats to get final imat
    imat = np.average(imats, axis=0)
    imat = imat.T
    
    if plot:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6,6))
        # Transpose back to match Olivier's plot...
        ax.imshow(imat.T, cmap="PiYG", aspect="auto", origin="lower")
        ax.set_title("imat shape: " + str(imat.shape), fontsize=12)
        plt.show()

    # Unfortunately, the dimensions of imat are hard-coded in the IDL script.
    # Show a warning if it doesn't match the parameters in settings.ini.
    n_channels = SETTINGS["AO"]["n_channels"]
    n_actuators = SETTINGS["AO"]["n_actuators"]
    n_subaps = SETTINGS["AO"]["n_subaps"]
    if imat.shape[0] != 2*n_subaps:
        warnings.warn("imat does not match the number of subapertures in settings.ini!" \
                      + " Proceed with caution.")
    if (imat.shape[1] != n_channels) and (imat.shape[1] != n_actuators):
        warnings.warn("imat does not match the number of actuators or channels in settings.ini!" \
                      + " Proceed with caution.")
    
    if fn_out:
        hdu = fits.PrimaryHDU(imat)
        hdu.header["COMMENT"] = "IDL-generated CACOFONI interaction matrix. Function call: " + cmd_str
        hdu.writeto(fn_out, overwrite=True)

    return imat


def make_cmat_from_imat(imat: NDArray, synth: bool, filternmodes: int = 1, pad: bool = True,
                        plot: bool = True, fn_out: str | None = None) -> NDArray:
    """Returns a control matrix. It is created by inverting the interaction matrix.
    This function may also create a synthetic cmat my fitting the influence functions
    to the data.

    Parameters
    ----------
    imat: nd_array
        Interaction matrix.
    synth: bool
        If True, creates a synthetic cmat. If False, uses empirical data only.
    filternmodes: int, optional
        Number of modes to filter out of the SVD.
    pad: bool, optional
        If True, pads the cmat to match the number of channels.
    plot: bool, optional
        If True, plots the cmat.
    fn_out: str or None, optional
        File name to save cmat to, including the file extension. If None, the
        file is not saved.

    Returns
    -------
    out: nd_array of shape (n_channels, 2*n_subaps)
        Control matrix.
    """
    assert abs(filternmodes)/filternmodes == 1, "filternmodes must be an integer"
    assert filternmodes >= 0, "filternmodes must be greater than or equal to 0"
    filternmodes = int(filternmodes)

    IDL = get_IDL()
    IDL.imat = imat.T

    # Create empirical cmat by inverting imat
    if not synth:
        IDL.run("cmat = invert_svd(imat, filternmodes=" + str(filternmodes) + ")")
        cmat = IDL.cmat
        cmat = cmat.T

    # Synthetic cmat
    else:
        # not implemented yet
        pass
    
    # Pad to match number of channels
    if pad:
        cmat = pad_cmat(cmat)

    if plot:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6,6))
        ax.imshow(cmat, cmap="PiYG", aspect="auto", origin="lower")
        ax.set_title("cmat shape: " + str(cmat.shape), fontsize=12)
        plt.show()

    if fn_out:
        cmat = np.float32(cmat)
        hdu = fits.PrimaryHDU(cmat)
        hdu.header["SYNTH"] = synth
        hdu.header["MODESFTD"] = filternmodes
        hdu.header["COMMENT"] = "Control matrix."
        hdu.writeto(fn_out, overwrite=True)

    return cmat


def pad_cmat(cmat: NDArray) -> NDArray:
    """Returns a cmat padded with 0s to match the number of channels. The output
    shape is expected to be (2*n_subaps, n_channels). The first dimension of the
    output will match that of the input. If it does not equal to 2*n_subaps, this
    function will show a warning.

    Parameters
    ----------
    cmat: nd_array of shape (k, m)
        Matrix to pad.
    
    Returns
    -------
    out: nd_array of shape (n_channels, m)
        Padded control matrix. m is expected to be equal to 2*n_subaps.
    """
    k, m = cmat.shape

    # Show a warning if it doesn't match settings.ini.
    n_channels = SETTINGS["AO"]["n_channels"]
    n_actuators = SETTINGS["AO"]["n_actuators"]
    n_subaps = SETTINGS["AO"]["n_subaps"]
    if m != 2*n_subaps:
        warnings.warn("cmat does not match the number of subapertures in settings.ini!" \
                      + " Proceed with caution.")
    if (k != n_channels) and (k != n_actuators):
        warnings.warn("cmat does not match the number of actuators or channels in settings.ini!" \
                      + " Proceed with caution.")
    
    # Pad the cmat along the actuator axis
    cmat_padded = np.zeros((n_channels, m))
    cmat_padded[:k, :] = cmat
    return cmat_padded


def southwell_points(Npts: int) -> NDArray:
    """Creates an array of points that sample the pupil evenly according to the
    sampling geometry shown in Southwell (1980) Fig 1A. Radius of pupil is 1.

    Parameters
    ----------
    Npts: int
        Number of points to sample along one direction.
    
    Returns
    -------
    out: np.ndarray
        Array of points in the Southwell geometry for a SHWFS.
    """
    subap_size = 2 / Npts
    xpts = np.arange(-1 + subap_size/2, 1, subap_size)
    ypts = np.arange(-1 + subap_size/2, 1, subap_size)
    X, Y = np.meshgrid(xpts, ypts, indexing="xy")
    return np.column_stack([X.ravel(), Y.ravel()])


def fried_points(Npts: int) -> NDArray:
    """
    """
    x = np.linspace(-1, 1, Npts+1)
    y = np.linspace(-1, 1, Npts+1)
    X, Y = np.meshgrid(x, y, indexing='xy')
    return np.array([X.ravel(), Y.ravel()]).T


def make_theoretical_imat_zernike(Nsub: int, Nmodes: int, scale: float,
                                  flip: int, imaka_order=True) -> NDArray:
    """Creates a theoretical interaction matrix for a Shack-Hartmann WFS using
    Noll Zernike polynomials.

    Parameters
    ----------
    Nsub: int
        Number of subapertures along one axis.
    Nmodes: int
        Number of Zernike modes to include in the interaction matrix. Piston is
        skipped.
    scale: float
        Scale factor to apply to the slopes.
    flip: int
        If 1, flips the sign of all indices with negative azimuthal frequency.
    imaka_order: bool, optional
        If True, the y-axis is indexed backwards and y slopes are given a sign
        flip. This follows the ordering used by the imaka RTC.

    Returns
    -------
    out: nd_array of shape (2*Nsub*Nsub, Nmodes)
        Theoretical Zernike interaction matrix for a SHWFS.
    """
    # Use Southwell geometry because we have the derivatives of Zernikes. So
    # we can directly evaluate the slope at the center of each subaperture.
    points = southwell_points(Nsub)

    # Create normalization coefficients
    norm = np.ones(Nmodes)
    norm *= scale

    # Flip sign of all indices with negative azimuthal frequency
    for k in range(Nmodes):
        m, n = noll_zernike_index(k + 2)
        if m < 0:
            norm[k] *= flip

    # Derivative matrices, plus 1 to skip piston
    gammax, gammay = make_gamma_matrices(Nmodes + 1)

    n_spots = points.shape[0]
    A = np.zeros((2*n_spots, Nmodes))

    for k in range(Nmodes):
        # Noll index would usually be k + 1... Skip piston, so k + 2.
        dervx, dervy = zernike_derv(k+2, gammax, gammay, points)
        for i in range(n_spots):
            A[i,k] = norm[k] * dervx[i]
            if imaka_order:
                A[i,k] = -1 * norm[k] * dervy[i][::-1]
            else:
                A[i+n_spots,k] = norm[k] * dervy[i]

    return A


def make_surface_interpolator(phi: NDArray) -> RBFInterpolator:
    """Interpolates a 2D surface, extrapolating over NaN values.

    Parameters
    ----------
    phi: nd_array of shape (Ny, Nx)
        2D surface to interpolate. NaN values will be extrapolated.
    Nx_out: int
        Number of points in the x-direction for the output grid.
    Ny_out: int
        Number of points in the y-direction for the output grid.
    
    Returns
    -------
    out: RBFInterpolator
        Surface interpolator object.
    """
    # Generate input grid of points
    Ny, Nx = phi.shape[0], phi.shape[1]
    xin = np.linspace(-1, 1, Nx)
    yin = np.linspace(-1, 1, Ny)
    Xin, Yin = np.meshgrid(xin, yin)
    points_in = np.array([Xin.ravel(), Yin.ravel()]).T

    # Mask out nan values in phi
    values = phi.ravel()
    valid_mask = ~np.isnan(values)
    valid_points = points_in[valid_mask]
    valid_values = values[valid_mask]

    # Use RBFInterpolator to allow for extrapolation...
    phi_itp = RBFInterpolator(valid_points, valid_values, kernel='thin_plate_spline')
    return phi_itp


def make_theoretical_imat_from_phase(modes: NDArray, Nsub: int, scale: float,
                                     mask: NDArray | None = None, imaka_order: bool = True) -> NDArray:
    """
    This function is useful for generating slope offsets to put an arbitrary
    shape onto the DM.
    
    Parameters
    ----------
    modes: nd_array of shape (Nmodes, Ny, Nx)
        Modes to use to create the imat. NaN values will be interpolated over and
        extrapolated.
    Nsub: int
        Number of subapertures along one axis.
    scale: float
        Scale factor to apply to the slopes.
    mask: nd_array of shape (Nsub*Nsub,), optional
        Mask to apply to the slopes, which should be True where subapertures should
        be masked out (set to zero). If None, no mask is applied.
    imaka_order: bool, optional
        If True, the y-axis is itdexed backwards and y slopes are given a sign
        flip. This follows the ordering used by the imaka RTC.
    
    Returns
    -------
    out: nd_array of shape (2*Nsub*Nsub, Nmodes)
        Theoretical interaction matrix for a SHWFS using the basis defined by
        the input modes.
    """    
    Nmodes = modes.shape[0]

    # Generate Fried points to sample the wavefront. Need to evaluate at the corners
    # and take the average slope for each subaperture. See Southwell (1980).
    points = fried_points(Nsub)

    mm2s = np.zeros((2*Nsub*Nsub, Nmodes))
    for n in range(Nmodes):
        
        phi_itp = make_surface_interpolator(modes[n])
        phi = phi_itp(points).reshape((Nsub+1, Nsub+1))
        
        slopesx = []
        slopesy = []
        # Note that i and j are flipped compared to Southwell
        for i in range(Nsub):
            
            if imaka_order:
                i = Nsub - i - 1  # need to index j backwards for 'imaka RTC ordering...

            for j in range(Nsub):
                sx = ( (phi[i,j+1] + phi[i+1,j+1])/2 - (phi[i,j] + phi[i+1,j])/2 )
                sy = ( (phi[i+1,j] + phi[i+1,j+1])/2 - (phi[i,j] + phi[i,j+1])/2 ) 

                if imaka_order:
                    sy *= -1

                slopesx.append(sx)
                slopesy.append(sy)

        slopesx = np.array(slopesx)
        slopesy = np.array(slopesy)

        if mask is not None:
            if mask.shape != (Nsub*Nsub):
                raise ValueError("Mask shape must match the number of subapertures: (Nsub*Nsub)")
            slopesx[mask] = 0
            slopesy[mask] = 0
        
        mm2s[:Nsub*Nsub, n] = slopesx
        mm2s[Nsub*Nsub:, n] = slopesy

    mm2s *= scale
    return mm2s