"""Helper functions for plotting.
"""

import numpy as np
import matplotlib.pyplot as plt

from numpy.typing import NDArray


def plot_cmds_irtfasm1(c: NDArray, F: NDArray) -> NDArray:
    """Plots actuator commands and the resulting surface shape for IRTF-ASM-1.

    Parameters
    ----------
    c: nd_array of size 36
        Actuator commands.
    F: nd_array of size (dx, dy, 36)
        Influence functions for the 36 actuators. The dimensions dx, dy corresponds
        to the size of the surface measurement (e.g., dx = dy = 47 for the HASO WFS).

    Returns
    -------
    out: nd_array of size (dx, dy)
        The projected surface shape. Units are the same as the surface measurements
        for the influence functions.
    """
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(10,5))
    # Plot actuator commands on a circle
    x = np.empty(36)
    y = np.empty(36)
    z = c.copy()
    ring_idx = [6, 18, 36]
    radius = [1, 2, 3]
    theta_offset = [2*np.pi/3, 2*np.pi/3 - 0.6, 2*np.pi/3 - 0.8]
    j1 = 0
    # Find the (x, y) coordinates for each point on the scatter plot that will
    # represent an actuator
    for i in range(3):
        j2 = ring_idx[i]
        r = radius[i]
        thetas = np.arange(0, 2*np.pi, 2*np.pi/(j2-j1))
        thetas += theta_offset[i]
        x[j1:j2] = r * np.cos(thetas)
        y[j1:j2] = r * np.sin(thetas)
        j1 = j2
    axs[0].scatter(x, y, c=z, s=500, cmap='seismic')
    # Put text labels for each actuator
    for i, z1 in enumerate(z):
        axs[0].annotate('{:.3f}'.format(z1), (x[i]+0.15, y[i]+0.15))
        if i > 9:
            axs[0].annotate('a' + str(i), (x[i]-0.18, y[i]-0.08), c='white')
        else:
            axs[0].annotate('a' + str(i), (x[i]-0.12, y[i]-0.08), c='white')
    axs[0].set_xlim(-3.8, 3.8)
    axs[0].set_ylim(-3.6, 3.6)
    axs[0].set_title("Normalized actuator commands", fontsize=12)

    # Plot wavefront that results from the given actuator commands
    phinew = np.dot(F, c)
    vmin = np.nanmin(phinew)
    vmax = np.nanmax(phinew)
    im = axs[1].imshow(phinew, vmin=vmin, vmax=vmax, cmap='seismic')
    plt.colorbar(im)
    axs[1].set_title("Surface from actuator commands", fontsize=12)

    plt.tight_layout()
    plt.show()

    return phinew