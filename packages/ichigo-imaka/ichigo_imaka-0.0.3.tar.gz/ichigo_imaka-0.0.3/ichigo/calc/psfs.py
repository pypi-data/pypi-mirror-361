"""Helper functions related to PSFs.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import hcipy

from numpy.typing import NDArray
from ichigo.calc.pupils import make_system_pupil
from ichigo.images import upsample_image
from ichigo.config import SETTINGS


def get_psf_coords(img: NDArray) -> tuple[int, int]:
    """Returns the coordinates of the PSF in the image.

    Parameters
    ----------
    img: nd_array of size (n, m)
        Image of the PSF.

    Returns
    -------
    cx: float
        x-coordinate of the center of the PSF in pixels.
    cy: float
        y-coordinate of the center of the PSF in pixels.
    """
    # I tried doing the center of mass of the array, but it didn't work well
    cy, cx = np.unravel_index(img.argmax(), img.shape)
    return cx, cy


def crop_image_to_psf(img: NDArray, s: int) -> NDArray:
    """Returns a cropped image centered on the PSF.

    Parameters
    ----------
    img: nd_array of size (n, m)
        Image of the PSF.
    s: int, optional
        Half size of the output image along one axis, in pixels.

    Returns
    -------
    out: nd_array of size (ns, ns)
        The cropped image centered on the PSF.
    """
    cx, cy = get_psf_coords(img)
    return img[cy-s:cy+s, cx-s:cx+s]


def subtract_background(img: NDArray, rin: int, rout: int, plot: bool = False) -> NDArray:
    """Returns a background-subtracted image. The background is computed by
    averaging over an annulus about the center of the PSF.

    Parameters
    ----------
    img: nd_array of size (n, m)
        Input image.
    rin: float, optional
        Inner radius of the annulus in pixels.
    rout: float, optional
        Outer radius of the annulus in pixels.
    plot: bool, optional
        If True, plots the annulus on top of the image.
    
    Returns
    -------
    result: nd_array of size (n, m)
        Background-subtracted input image.
    """
    # Generate a mask that is True inside the annulus
    ny, nx = img.shape[0], img.shape[1]
    x = np.linspace(0, nx, nx)
    y = np.linspace(0, ny, ny)
    cx, cy = get_psf_coords(img)  # center the annulus about the PSF
    annulus = np.logical_and((x[np.newaxis,:] - cx)**2 + (y[:,np.newaxis] - cy)**2 < rout**2, \
                         (x[np.newaxis,:] - cx)**2 + (y[:,np.newaxis] - cy)**2 > rin**2)
    Npix = np.sum(annulus)
    bg = np.nansum(img[annulus]) / Npix
    result = img - bg

    if plot:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5,4))
        ax.imshow(result, cmap='gray', origin='lower')
        annulus = patches.Annulus((cx, cy), (rout, rout), rout-rin, color='r', fill=False)
        ax.add_patch(annulus)
        fig.suptitle("Background subtracted image", fontsize=12)
        plt.tight_layout()
        plt.show()

    return result


def find_first_minimum(psf_dl: NDArray) -> int:
    """Returns the radius of the first minimum from the center.
    
    Parameters
    ---------
    psf_dl: nd_array of size (n, m)
        An array containing the Airy PSF.
    
    Returns
    -------
    out: int
        The radius in pixels.
    """
    a = np.sum(psf_dl, axis=0)
    # only look at values to the right of the center
    i0 = np.argmax(a)
    a = a[i0:]
    # iterate over the array until the next value is larger than the previous one
    i1 = 0
    while (i1 < len(a) - 2):
        if a[i1] < a[i1+1]:
            return i1
        i1 += 1
    if i1==len(a):
        raise Exception('Could not find first minimum of Airy PSF.')
    

def make_psf_dl(img_size_px: int, flux_in: float | None = None, pupil_grid_px: int = 256, pupil_grid_size: float = 1.4) -> NDArray:
    """Creates a diffraction-limited PSF for the system defined in settings.ini.

    Parameters
    ----------
    img_size_px: int
        Size of the output image in pixels.
    flux_in: float, optional
        Total flux of the input PSF, which is used to normalize the D-L PSF. If
        None, the peak of the D-L PSF is set to 1.
    pupil_grid_px: int, optional
        Number of pixels in the pupil grid.
    pupil_grid_size: float, optional
        Size of the pupil grid in pupil diameters.
    
    Returns
    -------
    result: nd_array of size (img_size_px, img_size_px)
        The diffraction-limited PSF.
    """
    assert pupil_grid_px <= 2048, "Pupil grid size cannot exceed 2048."

    pupil = make_system_pupil(pupil_grid_px, pupil_grid_size)
    pupil_grid = pupil.pupil_grid

    # Size of diffraction core in pixels
    # 2.25 is a fudge factor - the size of lambda f/D appears to be too small in
    # hcipy by this amount
    core_size = 2.25 * SETTINGS["IMAGING"]["resolution_element"]
    # Half size of the image in diffraction widths
    img_half_size = img_size_px / core_size / 2

    wavefront = hcipy.Wavefront(pupil.get_pupil(), 1)
    focal_grid = hcipy.make_focal_grid(core_size, img_half_size)
    prop = hcipy.FraunhoferPropagator(pupil_grid, focal_grid)
    
    focal_image = prop.forward(wavefront)

    if flux_in:
        result = focal_image.intensity * flux_in / focal_image.intensity.sum()
    else:
        result = focal_image.intensity / focal_image.intensity.max()
    result = np.array(result.shaped)

    return result


def calc_strehl(psf_in: NDArray, preprocess: bool = True, upsamp: int = 4,
                plot: bool = False) -> float:
    """Returns the Strehl ratio. The Strehl ratio is computed by upsampling the
    the input and D-L PSFs via a 2D spline interpolator. Then, this function takes
    the ratio of the maxima of these PSFs.

    psf_in must be background subtracted or this will not work!

    Parameters
    ----------
    psf_in: nd_array of size (n, m)
        Input PSF.
    preprocess: bool, optional
        If True, the image is cropped to have a width of 16 * the diffraction-limited
        PSF and the background is subtracted.
    upsamp: int, optional
        Factor to upsample the data by.
    plot: bool, optional
        Plots the interpolated PSFs if True.
    
    Returns
    -------
    strehl: float
        The computed Strehl ratio.
    """
    assert len(psf_in.shape) == 2, "Input PSF must be 2D."
    assert psf_in.shape[0] == psf_in.shape[1], "Input PSF must be square."

    flux_in = np.nansum(psf_in)

    if preprocess:
        core = SETTINGS["IMAGING"]["resolution_element"]
        core = round(core)
        psf_in = crop_image_to_psf(psf_in, 8*core)
        psf_in = subtract_background(psf_in, 6*core, 8*core, plot=False)

    psf_dl = make_psf_dl(psf_in.shape[0], flux_in=flux_in)

    # Interpolate and compute strehl ratio
    psf_in_itp = upsample_image(psf_in, upsamp)
    psf_dl_itp = upsample_image(psf_dl, upsamp)

    strehl = np.max(psf_in_itp) /  np.max(psf_dl_itp)

    if plot:
        fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(8,4))
        
        axs[0].imshow(psf_in, cmap='gray', origin='lower')
        axs[0].axis('off')
        axs[0].set_title("Input PSF (Interpolated)")

        axs[1].imshow(psf_dl, cmap='gray', origin='lower')
        axs[1].axis('off')
        axs[1].set_title("Theoretical Diffraction-Limited PSF")
        fig.suptitle("Strehl Ratio: " + '{:.2f}'.format(strehl), fontsize=12)
        plt.tight_layout()
        plt.show()

    return strehl


def calc_strehl_marechal(a_j: NDArray, wl: float) -> float:
    """Returns the Strehl ratio computed from the Marechal approximation.
    
    Parameters
    ----------
    a_j: nd_array
        An array containing the coefficients [a_1, a_2, ..., a_j] of the Zernike
        modes, in microns.
    wl: float
        Wavelength in microns.
    
    Returns
    -------
    out: float
        The approximate Strehl ratio.
    """
    s_tot = np.sqrt(np.sum(a_j**2))
    s_tot = s_tot * 2*np.pi/wl
    return np.exp(-1*s_tot**2)


def encircled_energy():
    # Fit a gaussian
    # get radius from gaussian
    pass


def speckles():
    pass