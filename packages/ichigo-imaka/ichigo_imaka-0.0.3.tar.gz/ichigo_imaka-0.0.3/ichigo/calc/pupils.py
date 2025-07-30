"""Generates aperture masks as hcipy objects.
"""

import numpy as np
import hcipy

from ichigo.config import SETTINGS


class CircularPupil:
    """Class for generating circular pupil masks with spiders and obstruction.
    """

    def __init__(self, diameter: float, obsc_ratio: float, num_spiders: int, spider_width: float,
                 grid_px: int, grid_size: float) -> None:
        """Initializes the CircularPupil object.

        Parameters
        ----------
        diameter: float
            Diameter of the pupil in meters.
        obsc_ratio: float
            Ratio of the central obscuration to the pupil diameter.
        num_spiders: int
            Number of spiders in the pupil.
        spider_width: float
            Width of the spiders in meters.
        grid_px: int
            Number of pixels in the pupil grid.
        grid_size: float
            Size of the grid in pupil diameters.

        Returns
        -------
        None
        """
        self.diameter = diameter
        self.obsc_ratio = obsc_ratio
        self.num_spiders = num_spiders
        self.spider_width = spider_width
        self.aperture = hcipy.make_obstructed_circular_aperture(
            pupil_diameter=diameter,
            central_obscuration_ratio=obsc_ratio,
            num_spiders=num_spiders,
            spider_width=spider_width
        )

        self.update_pupil_grid(grid_px, grid_size)
    
    def update_pupil_grid(self, grid_px: int, grid_size: float) -> None:
        """Updates the pupil grid.

        Parameters
        ----------
        grid_px: int
            Number of pixels in the pupil grid.
        grid_size: float
            Size of the grid in pupil diameters.
        """
        grid_diameter = grid_size * self.diameter
        self.pupil_grid = hcipy.make_pupil_grid(grid_px, diameter=grid_diameter)

    def get_pupil(self, oversamp: float = 1) -> hcipy.field.Field:
        """Evaluates the pupil mask on the pupil grid.

        Parameters
        ----------
        oversamp: float, optional
            Factor by which to oversample the pupil mask.
        
        Returns
        -------
        out: hcipy.field.Field
            The pupil mask.
        """
        return hcipy.evaluate_supersampled(self.aperture, self.pupil_grid, oversamp)


def make_system_pupil(grid_px: int, grid_size: float) -> CircularPupil:
    """Creates a pupil mask based on the pupil type defined in settings.ini.

    Parameters
    ----------
    grid_px: int
        Number of pixels in the pupil grid.
    grid_size: float
        Size of the grid in pupil diameters. E.g., if the diameter is 10 meters
        and grid_size = 1.4, then the grid is 14 meters across.
    """
    pupil_type = SETTINGS["IMAGING"]["pupil"]

    pupils_dict = {
        "irtf": make_irtf_pupil(grid_px, grid_size),
        "uh88": make_uh88_pupil(grid_px, grid_size)
    }
    try:
        return pupils_dict[pupil_type]
    except KeyError:
        raise KeyError("Pupil type in settings.ini is not recognized. Please choose" \
                       + "from: " + ", ".join(pupils_dict.keys()) )


def make_irtf_pupil(grid_px: int, grid_size: float) -> CircularPupil:
    """Makes the IRTF pupil.
    """
    diameter = 3
    obsc_ratio = 0.12
    num_spider = 4
    spider_width = 0.03
    return CircularPupil(diameter, obsc_ratio, num_spider, spider_width, grid_px, grid_size)


def make_uh88_pupil(grid_px: int, grid_size: float) -> CircularPupil:
    """Makes the UH88 pupil.
    """
    diameter = 2.2
    obsc_ratio = 0.3 #?
    num_spider = 4
    spider_width = 0.03
    return CircularPupil(diameter, obsc_ratio, num_spider, spider_width, grid_px, grid_size)