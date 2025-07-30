"""Functions for importing and manipulating images.
"""

import os
import glob
import numpy as np

from astropy.io import fits
from numpy.typing import NDArray
from scipy.interpolate import RectBivariateSpline
from PIL import Image


def get_image(fn: str) -> NDArray:
    """Returns an image file as a numpy array.

    Parameters
    ----------
    fn: str
        Path to the image.

    Returns
    -------
    out: nd_array of size (n, m)
        A 2D array containing the PSF.
    """
    if fn.lower().endswith('.fits'):
        img = fits.getdata(fn, ext=0)
    else:
        try:
            img = Image.open(fn).convert('L')  # convert to grayscale
        except:
            raise ValueError("File type cannot be read as image.")
    return np.array(img)


def get_images_in_path(path: str, recursive: bool = False, extensions: list[str] = ["fits"]) -> NDArray:
    """Returns an array containing all of the images in the specified directory.
    All images must have the same shape.

    Parameters
    ----------
    path: str
        Directory containing images to combine.
    recursive: bool, optional
        If True, the directory is searched recursively.
    extensions: list of str, optional
        List of file extensions to include (upper or lowercase). Default is ["fits"].

    Returns
    -------
    out: nd_array of size (k, n, m)
        Array containing k images of size (n, m),
    """
    fnames = []
    for ext in extensions:
        # Search for both lower and upper case extensions
        queries = [os.path.join(path, '*.' + e) for e in (ext.lower(), ext.upper())]
        results = [glob.glob(query, recursive=recursive) for query in queries]
        fnames += results[0] + results[1]

    images = []
    for fname in fnames:
        img = get_image(fname)
        images.append(img)
    return np.array(images)


def stack_images(path: str, ext: str, path_bg: str | None = None, fn_out: str | None = None) -> NDArray:
    """Returns a stacked (summed) image from the images in the specified directory.
    All images must have the same dimensions.

    Parameters
    ----------
    path: str
        Directory containing images to combine.
    ext: str
        File extension of the images to stack.
    path_bg: str or None, optional
        Path to background images. If not None, this function creates a background
        frame by averaging all of the images in path_bg. This frame is subtracted
        from each image before stacking.
    fn_out: str or None, optional
        File name to save the stacked image to, including the file extension. If
        None, the file is not saved.

    Returns
    -------
    out: nd_array
        The stacked image.
    """
    imgs = get_images_in_path(path, extensions=[ext])

    if path_bg is not None:
        imgs_bg = get_images_in_path(path_bg)
        bg_averaged = np.average(imgs_bg, axis=0)
        imgs = imgs - bg_averaged[np.newaxis, :, :]

    img_stack = np.sum(imgs, axis=0)

    if fn_out:
        ext = os.path.splitext(fn_out)[1]
        ext = ext.lower()
        if ext == ".fits":
            hdu = fits.PrimaryHDU(img_stack)
            hdu.header['comment'] = "Averaged over the files in " + path
            hdu.writeto(fn_out, overwrite=True)
        else:
            img_to_save = Image.fromarray(img_stack)
            img_to_save.save(fn_out)
    
    return img_stack
    

def upsample_image(img: NDArray, s: int) -> NDArray:
    """Returns an image upsampled via 2D b-spline interpolation.

    Parameters
    ----------
    img: nd_array of size (n, m)
        Image to upsample.
    s: int
        Factor to upsample the image by.

    Returns
    -------
    out: nd_array of size (n*s, m*s)
        Upsampled image.
    """
    # x and y are flipped in RectBivariateSpline... They seem to be i and j...
    xi = np.arange(img.shape[0])
    yi = np.arange(img.shape[1])
    # interp2d is depreciated as of scipy 1.10.0. RegularGridInterpolator is recommended
    # for grid data but it is *excruciatingly* slow so I am using
    # RectBivariateSpline instead
    interp = RectBivariateSpline(xi, yi, img)
    xnew = np.linspace(xi[0], xi[-1], xi[-1]*s)
    ynew = np.linspace(yi[0], yi[-1], yi[-1]*s)
    return interp(xnew, ynew)