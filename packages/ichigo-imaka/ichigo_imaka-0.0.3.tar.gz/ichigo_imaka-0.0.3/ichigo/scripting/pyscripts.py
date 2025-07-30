"""Python scripts. This module is accessed by the scripting CLI. Functions with
names that begin with a '_' are ignored by the CLI and cannot be accessed by the
user.

NOTE: The scripting CLI allows the user to reload this module without restarting
the Python kernel. This is done via the built-in function importlib.reload, which
will overwrite old definitions but will not remove functions that have been deleted.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import ichigo.calc.cmat as ch
import ichigo.calc.buffers as sb

from astropy.io import fits
from astropy.modeling import models, fitting
from numpy.typing import NDArray
from ichigo.servers import *
from ichigo.strmanip import print_color, get_timestamp
from ichigo.config import SETTINGS

def update_dmflat(servers_dict: dict[str, Server], path_old_rtc: str, path_new_rtc: str,
                  rtc_alias: str = "rtc", ehu_alias: str = "ehu") -> None:
    """Creates a new DM flat in the ~/cals/ directory of the RTC.

    Parameters
    ----------
    servers_dict: dict of ichigo.servers.Server or a child of this class
        Defines a mapping between aliases and Server object. For example,
        {"rtc": instance of ImakaRTCServer}
    path_old_rtc: str
        Path of the file containing the old flat commands on the RTC.
    path_new_rtc: str
        Path of the new file to save to on the RTC.
    rtc_alias: str, optional
        Alias of the RTC in servers_dict.
    ehu_alias: str, optional
        Alias of ehu (the telemetry server) in servers_dict.

    Returns
    -------
    None
    """
    # Need ehu to save telemetry and data from the RTC
    rtc = servers_dict[rtc_alias]
    ehu = servers_dict[ehu_alias]
    assert isinstance(rtc, ImakaRTCServer), "rtc must be an instance of ImakaRTCServer"
    assert isinstance(ehu, EhuServer), "ehu must be an instance of EhuServer"

    print("Saving 'imaka data and copying to local...")
    newcmd = ehu.get_average_actuator_cmd()
    print("Copying old flat commands to local...")
    path_oldflat_local = SETTINGS["RESOURCES"]["dm_flat"]
    rtc.sftp_get(path_old_rtc, path_oldflat_local)

    # Add the commands together
    oldflat = fits.getdata(path_oldflat_local)
    newflat = oldflat + newcmd
    
    # Save the data and SFTP the file to the RTC
    print("Saving new flat commands to RTC...")
    hdu = fits.PrimaryHDU(newflat)
    hdu.writeto(SETTINGS["RESOURCES"]["dm_flat"], overwrite=True)
    rtc.sftp_put(SETTINGS["RESOURCES"]["dm_flat"], path_new_rtc)

def generate_cacofoni(servers_dict: dict[str, Server], gain: float, leak: float, 
                      pbgain: float, minfreq: float, maxfreq: float, synth: bool,
                      fn_append: str = "a", filternmodes: int = 1, n_aocb: int = 3,
                      rtc_alias: str = "rtc", ehu_alias: str = "ehu",
                      **kwargs) -> tuple[NDArray, NDArray]:
    """Makes a CACOFONI cmat and sends to it to the RTC.

    This assumes that the appropriate playback buffer is loaded into the RTC.

    Parameters
    ----------
    servers_dict: servers_dict: dict of asmtools.servers.network.Server or a child of this class
        Defines a mapping between aliases and Server object. For example,
        {"rtc": instance of ImakaRTCServer}
    gain: float
        Gain for the loop. Set to 0 to run in open loop.
    leak: float
        Leak for the loop.
    pbgain: float
        Playback buffer gain.
    minfreq: float
        Minimum frequency for the CACOFONI matrix.
    maxfreq: float
        Maximum frequency for the CACOFONI matrix.
    synth: bool
        If True, generates a synthetic cmat. If False, empirical cmat only.
    fn_append: str, optional
        String to append to the file name. Set to "a" by default.
    filternmodes: int, optional
        Number of modes to filter.
    n_aocb: int, optional
        Number of aocbs to average over. Set to 3 by default.
    rtc_alias: str, optional
        Alias of the RTC in servers_dict. Set to "rtc" by default.
    ehu_alias: str, optional
        Alias of ehu (the telemetry server) in servers_dict. Set to "ehu" by default.
    **kwargs: optional
        Parameters to pass to the make_cacophony_imat function. These are any optional
        parameters that would be passed to the IDL function make_cacophony.

    Returns
    -------
    imat: nd_array
        Interaction matrix.
    cmat: nd_array
        Control matrix.
    """
    # So we don't accidentally request a very large number of telemetry files...
    assert n_aocb < 50, "Number of requested telemetry files must be < 50"

    # Need ehu to save telemetry and data from the RTC
    rtc = servers_dict[rtc_alias]
    ehu = servers_dict[ehu_alias]
    assert isinstance(rtc, ImakaRTCServer), "rtc must be an instance of ImakaRTCServer"
    assert isinstance(ehu, EhuServer), "ehu must be an instance of EhuServer"

    # Get telemetry
    rtc.set_loop_pid(gain, leak, pbgain)
    fnames, indices = ehu.save_aocbs_autoidx(n_aocb)
    aocb_data, fns_aocb = ehu.get_aocbs_by_index(indices)

    # Create CACOFONI matrices using Olivier's IDL routines
    fn_imat = "imat.cacofoni." + get_timestamp(date_only=True) + fn_append + ".fits"
    fn_cmat = "cmat.cacofoni." + get_timestamp(date_only=True) + fn_append + ".fits"
    path_local_imat = os.path.join(SETTINGS["PATHS"]["temp"], fn_imat)
    path_local_cmat = os.path.join(SETTINGS["PATHS"]["temp"], fn_cmat)

    try:
        imat = ch.make_cacophony_imat(fns_aocb, minfreq, maxfreq, fn_out=path_local_imat, **kwargs)
        cmat = ch.make_cmat_from_imat(imat, synth, filternmodes=filternmodes, fn_out=path_local_cmat)

    except Exception as e:
        # Make sure the pbgain is reset to 0
        rtc.set_loop_pid(0, 1, 0)
        raise e

    # SFTP files to the RTC
    path_rtc_imat = rtc.cals_path + fn_imat
    path_rtc_cmat = rtc.cals_path + fn_cmat
    rtc.sftp_put(fn_imat, path_rtc_imat)
    rtc.sftp_put(fn_cmat, path_rtc_cmat)
    print_color("CACOFONI cmat saved to the RTC in: " + path_rtc_cmat, "green")

    rtc.open_loop_noleak()
    return imat, cmat

def focus_run(servers_dict: dict[str, Server], focus_values: list | NDArray, t: float,
              g: float = 0, n_ave: int = 1, offsets: list | NDArray | None = None,
              plot: bool = True, load_result: bool = False) -> float:
    """Scans through focus and finds the best focus value.

    Parameters
    ----------

    """
    rtc = servers_dict["rtc"]
    nuc = servers_dict["nuc"]
    assert isinstance(rtc, ImakaRTCServer), "rtc must be an instance of ImakaRTCServer"
    assert isinstance(nuc, WindowsNUCServer), "nuc must be an instance of WindowsNUCServer"

    Nmodes = rtc.zer_to_slopes.shape[1]
    if offsets is None:
        base_offsets = np.zeros(Nmodes)
    else:
        assert len(offsets) < Nmodes, "Number of offsets cannot exceed number of modes defined in RTC zer-to-slopes"
        offsets = np.array(offsets)
        base_offsets = np.zeros(Nmodes)
        base_offsets[:len(offsets)] = offsets

    assert all(x < y for x, y in zip(focus_values, focus_values[1:])), "Focus values must increase monotonically"
    focus_values = np.array(focus_values)
    
    maxima = np.zeros_like(focus_values)
    for i, val in enumerate(focus_values):

        print_color(f"Loading focus offset {val}...", "cyan")
        new_offsets = np.zeros(Nmodes)
        new_offsets[2] = val
        rtc.load_slope_offsets(new_offsets + base_offsets)

        img = nuc.sharpcap_get_one_image(t, g, n_ave)
        imgmax = np.nanmax(img)
        maxima[i] = imgmax
        print_color(f"Found maximum {imgmax} at focus value {val}\n", "cyan")

    p_init = models.Gaussian1D(mean=np.mean(focus_values), amplitude=maxima.max(), stddev=np.std(focus_values))
    fit_p = fitting.DogBoxLSQFitter()
    p = fit_p(p_init, focus_values, maxima)
    best_focus = p.mean.value

    if plot:
        x_model = np.linspace(focus_values[0], focus_values[-1], 50)
        y_model = p(x_model)

        plt.figure()
        plt.scatter(focus_values, maxima, c='plum')
        plt.plot(x_model, y_model, c='darkblue', label="Gaussian fit")
        plt.vlines(best_focus, maxima.min(), y_model.max(), color='red', linestyle='--', label="Best focus: " + '{:.4f}'.format(best_focus))
        plt.xlabel("Focus value")
        plt.ylabel("Image maximum")
        plt.legend()
        plt.show()

    if best_focus > focus_values.max() or best_focus < focus_values.min():
        raise ValueError(f"Best focus value is out of range. Computed {best_focus}")
    print_color("Best focus is " + str(best_focus) + f" with amplitude {p.amplitude.value}", "green")

    if load_result:
        new_offsets = np.zeros(Nmodes)
        new_offsets[2] = best_focus
        rtc.load_slope_offsets(new_offsets + base_offsets)
    return best_focus

def make_cosine_modes_slopes_buffer(servers_dict: dict[str, Server], fn_out: str,
                             mode_idxs: list[int], freqs: list[float], amps: list[float],
                             phases: list[float] | None = None, shifts: list[float] | None = None, 
                             basis: str = "zernike", length: float | None = None,
                             plot: bool = True, **kwargs) -> None:
    """Creates slope offset buffers for the given focus value.

    Parameters
    ----------
    servers_dict: dict[str, Server]
        Dictionary of server instances.
    """
    rtc = servers_dict["rtc"]
    assert isinstance(rtc, ImakaRTCServer), "rtc must be an instance of ImakaRTCServer"

    Nmodes = len(mode_idxs)
    Nmax = SETTINGS["AO"]["n_so_modes"]
    assert Nmodes > 0, "At least one mode index must be provided."
    assert Nmodes <= Nmax, "No more than 9 modes can be modulated at once."

    phases = phases or [0.] * Nmodes
    shifts = shifts or [0.] * Nmodes
    
    # Generate the slope offsets buffer
    t_end = length or 1 / min(freqs)
    loop_rate = SETTINGS["AO"]["loop_rate"]
    ts = np.arange(0, t_end, 1/loop_rate)
    Nsamp = len(ts)
    Nslopes = SETTINGS["AO"]["n_subaps"] * 2

    slopes = np.zeros((Nmax, Nsamp, Nslopes), dtype=np.float32)
    for i, idx in enumerate(mode_idxs):
        slopes[i] = sb.make_modal_slope_offsets(
            "cosine", basis, idx, freqs[i],
            amps[i], shifts[i], phases[i],
            length=t_end, **kwargs
        )
    print_color("Created slope offset buffer with shape: " + str(slopes.shape), "green")
    
    # Save to FITS file and write to the RTC
    path_local = os.path.join(SETTINGS["PATHS"]["temp"], fn_out)
    hdu = fits.PrimaryHDU(slopes)
    hdu.header["SHAPE"] = "cosine"
    hdu.header["MODES"] = str(mode_idxs)
    hdu.header["FREQS"] = str(freqs)
    hdu.header["AMPS"] = str(amps)
    hdu.header["SHIFTS"] = str(shifts)
    hdu.header["PHASES"] = str(phases)
    hdu.writeto(path_local, overwrite=True)

    path_rtc = rtc.cals_path + f"pbsoff/{fn_out}"
    print_color("Transferring to RTC: " + path_rtc, "cyan")
    rtc.sftp_put(path_local, path_rtc)

    # Show the ramps
    if plot:
        ts = np.arange(0, t_end, 1 / SETTINGS["AO"]["loop_rate"])
        plt.figure(figsize=(6,4))
        for i, idx in enumerate(mode_idxs):
            y = sb.cosine_wave(ts, freqs[i], amps[i], shifts[i], phases[i])
            plt.plot(ts, y, label=f"mode_idx={idx}")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.tight_layout()
        plt.show()
    

def make_chopping_slopes_buffer(servers_dict: dict[str, Server], fn_out: str, modes: list[int],
                            ramp_sizes: list[float], freqs: list[float], amps: list[float],
                            phases: list[float] | None = None, shifts: list[float] | None = None, 
                            length: float | None = None, plot: bool = True, **kwargs) -> None:
    """Creates chopping slope offset buffers. 
    """
    rtc = servers_dict["rtc"]
    assert isinstance(rtc, ImakaRTCServer), "rtc must be an instance of ImakaRTCServer"

    Nmodes = len(modes)
    Nmax = SETTINGS["AO"]["n_so_modes"]
    assert Nmodes > 0, "At least one mode index must be provided."
    assert Nmodes <= Nmax, "No more than 9 modes can be modulated at once."

    phases = phases or [0.] * Nmodes
    shifts = shifts or [0.] * Nmodes
    
    # Generate the slope offsets buffer
    t_end = length or 1 / min(freqs)
    loop_rate = SETTINGS["AO"]["loop_rate"]
    ts = np.arange(0, t_end, 1/loop_rate)
    Nsamp = len(ts)
    Nslopes = SETTINGS["AO"]["n_subaps"] * 2

    slopes = np.zeros((Nmax, Nsamp, Nslopes), dtype=np.float32)
    for i, val in enumerate(modes):

        # Do both modes at once if val == 2
        if val == 2:
            slopes_tip = sb.make_modal_slope_offsets(
                "trapezoid", "zernike", 0, freqs[i], amps[i], shifts[i], phases[i],
                ramp_size=ramp_sizes[i], length=t_end, **kwargs
            )
            slopes_tilt = sb.make_modal_slope_offsets(
                "trapezoid", "zernike", 1, freqs[i], amps[i], shifts[i], phases[i],
                ramp_size=ramp_sizes[i], length=t_end, **kwargs
            )
            # modes are added in quadrature so normalize...
            slopes[i] = (slopes_tip + slopes_tilt) / np.sqrt(2)
        
        else:
            slopes[i] = sb.make_modal_slope_offsets(
                "trapezoid", "zernike", val, freqs[i],
                amps[i], shifts[i], phases[i],
                ramp_size=ramp_sizes[i], length=t_end, **kwargs
            )
    print_color("Created slope offset buffer with shape: " + str(slopes.shape), "green")
    
    # Save to FITS file and write to the RTC
    path_local = os.path.join(SETTINGS["PATHS"]["temp"], fn_out)
    hdu = fits.PrimaryHDU(slopes)
    hdu.header["SHAPE"] = "trapezoid"
    hdu.header["MODES"] = str(modes)
    hdu.header["FREQS"] = str(freqs)
    hdu.header["AMPS"] = str(amps)
    hdu.header["SHIFTS"] = str(shifts)
    hdu.header["PHASES"] = str(phases)
    hdu.header["RAMPS"] = str(ramp_sizes)
    hdu.header["COMMENT"] = "MODES refers to whether the slopes are for tip (0), tilt(1), or both at once (2)."
    hdu.writeto(path_local, overwrite=True)

    path_rtc = rtc.cals_path + f"pbsoff/{fn_out}"
    print_color("Transferring to RTC: " + path_rtc, "cyan")
    rtc.sftp_put(path_local, path_rtc)

    # Show the ramps
    if plot:
        wave_func = np.vectorize(sb.trapezoid_wave)
        ts = np.arange(0, t_end, 1 / SETTINGS["AO"]["loop_rate"])

        plt.figure(figsize=(6,4))
        for i, val in enumerate(modes):
            y = wave_func(ts, freqs[i], amps[i], shifts[i],
                          phases[i], ramp_size=ramp_sizes[i])
            plt.plot(ts, y, label=f"mode={val}")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.tight_layout()
        plt.show()

def _compute_strehl(servers_dict: dict[str, Server]) -> tuple[float, NDArray]:
    """Takes an image and shows it with the computed Strehl ratio.

    Parameters
    ----------
    None

    Returns
    -------
    strehl: float
        The Strehl ratio.
    img: nd_array
        Image used to compute the Strehl ratio.
    """
    return (0, np.zeros(1))