"""Class for closing the loop with FELIX.
NOTE: This package was never intended to go particularly fast.

TODO:
- Implement mirror modes? The current mm2a matrix does not include piston
  whereas the z2a matrix does (or should) since the latter is used for piston
  filtering.
"""

import os
import numpy as np
import warnings

from astropy.io import fits
from numpy.typing import NDArray, ArrayLike
from ichigo.strmanip import print_color, get_timestamp
from ichigo.servers import create_server, ImakaRTCServer, FELIXHelperServer
from ichigo.managers import Manager
from ichigo.config import SETTINGS

class FELIXLoopManager(Manager):
    """Recieves data from FELIX and sends commands to the RTC. This class is
    supposed to function as a "pseudo-RTC" for FELIX but is not designed to run
    in real time.

    Attributes
    ----------

    """
    def __init__(self, fn_cmat: str | None = None, rtc_alias: str = "rtc",
                 felix_alias: str = "felix") -> None:
        """Initializes the FELIXLoopManger object.

        Parameters
        ----------
        fn_cmat: str or None, optional

        Returns
        -------
        None
        """
        super().__init__()

        self.imat = None
        self.cmat = None
        self.basis = None
        if fn_cmat:
            self.update_cmat(fn_cmat)

        self.loop_counter = 0
        self.a_prev = None  # This will be updated when the cmat is set
        self.a_flat = None
        
        # Add the relevant servers
        expected_types = {
            rtc_alias: ImakaRTCServer,
            felix_alias: FELIXHelperServer
            }

        for alias, server_type in expected_types.items():
            server = create_server(alias)
            assert isinstance(server, server_type), f"{alias} server must be of type {server_type}"
            self.add_server(alias, server)

        self.rtc: ImakaRTCServer = self.get_server(rtc_alias)
        self.felix: FELIXHelperServer = self.get_server(felix_alias)

        self.tel_slopes = []
        self.tel_cmds = []
        self.tel_timestamps = []

    def dump_telemetry(self, fname: str) -> None:
        """Dumps telemetry to a file, including measured slopes, timestamps, and commands.
        """
        slopes = np.array(self.tel_slopes)
        cmds = np.array(self.tel_cmds)
        timestamps = np.array(self.tel_timestamps)

        hdu1 = fits.PrimaryHDU(slopes)
        hdu2 = fits.ImageHDU(cmds)
        hdu3 = fits.ImageHDU(timestamps)
        hdulist = fits.HDUList([hdu1, hdu2, hdu3])

        hdu1.header["UTCTIME"] = get_timestamp()
        hdu1.header["BASIS"] = self.basis

        hdu1.header["COMMENT"] = "slopes"
        hdu2.header["COMMENT"] = "commands"
        hdu3.header["COMMENT"] = "timestamps"

        path = os.path.join(SETTINGS["PATHS"]["felix"], fname + ".fits")
        hdulist.writeto(path)
        print_color(f"Telemetry saved to {path}", "cyan")

        self.tel_slopes = []
        self.tel_cmds = []
        self.tel_timestamps = []
        

    def _retrieve_stored_data(self, fname: str, ext: int = 0) -> tuple[NDArray, str]:
        """Attempts to retrieve a FITS file as either an absolute path or a file
        name in the FELIX data directory (defined in settings.ini). The data are
        retrieved from extension 0.

        Parameters
        ----------
        fname: str
            File name to retrieve.

        Returns
        -------
        data: nd_array
            Data from the FITS file. 
        path: str
            Absolute path to the file.
        """
        # Check if fname exists in the FELIX data directory. If not, try as
        # an absolute path.
        abs_path = os.path.join(SETTINGS["PATHS"]["felix"], fname)
        if not os.path.isfile(abs_path):
            print_color("This doesn't seem to exist in the FELIX resources directory. " \
                    + "Attempting to open as an absolute path: " + fname, "yellow")
            abs_path = fname
        # Try to load the file - it will fail here if the file doesn't exist.
        data = fits.getdata(abs_path, ext=ext)
        return data, abs_path

    def update_cmat(self, fname: str) -> None:
        """Updates the control matrix.

        Parameters
        ----------
        fn: str
            File name of the control matrix. Either an absolute path or a
            file in the FELIX data directory.

        Returns
        -------
        None
        """
        self.cmat, abs_path = self._retrieve_stored_data(fname, 0)
        self.a_prev = np.zeros(self.cmat.shape[0])
        # Update the modal basis
        hdr = fits.open(abs_path)[0].header
        self.basis = hdr["BASIS"]

    def update_imat(self, fname: str) -> None:
        """Updates the interaction matrix. This is used to generate slope
        offsets.

        Parameters
        ----------
        fn: str
            File name of the interaction matrix. Either an absolute path or a
            file in the FELIX data directory.

        Returns
        -------
        None
        """
        self.imat, abs_path = self._retrieve_stored_data(fname, 0)
        self.a_prev = np.zeros(self.imat.shape[1])
        # Update the modal basis
        hdr = fits.open(abs_path)[0].header
        if (self.basis is not None and hdr["BASIS"] != self.basis):
            raise ValueError(f"imat does not match basis of cmat ({self.basis}): {abs_path}")
        self.basis = hdr["BASIS"]

    def update_cal_file(self, fname: str) -> None:
        """Updates the calibration slopes. This is used to generate slope offsets.
        NOTE: This does not check if the slopes are in the correct basis!
        """
        slopes, abs_path = self._retrieve_stored_data(fname, 0)
        self.felix.update_cal_slopes(slopes)

    def make_imat_empirical(self, poke: float, n_ave: int, n_modes: int, basis: str = "zernike", update: bool = True, 
                                name: str = "felix") -> tuple[NDArray, NDArray]:
        """Creates a modal interaction matrix by injecting Zernikes onto the ASM
        and measuring the response of the WFS.

        Parameters
        ----------
        poke: float
            Poke command. Must be < 0.2 to avoid saturation.
        n_ave: int
            Number of frames to average per measurement.
        n_modes: int
            Number of modes.
        basis: str
            Basis set to use. Options: "zernike" or "mirror"
        update: bool
            If True, updates the cmat used for the control loop.
        name: str
            Name of the imat and cmat.
        
        Returns
        -------
        imat: nd_array
            Interaction matrix.
        cmat: nd_array
            Control matrix, which is the (pseudo-) inverse of the imat.
        """
        assert np.abs(poke) < 0.5, "Poke amount must be less than 0.4"

        # Loop must be open to project modes
        self.rtc.open_loop_noleak()
        # Reset previous command as number of modes may have changed
        self.a_prev = np.zeros(n_modes)

        # Construct the interaction matrix. Dimensions are determined by number
        # of modes and number of slopes (spots * 2).
        imat = np.zeros((2 * SETTINGS["FELIX"]["n_spots"], n_modes))
        for i in range(n_modes):
            
            print_color("Poking mode " + str(i), "cyan")

            # + Poke
            a = np.zeros(n_modes)
            a[i] = poke
            self.apply_modes(a, basis, open=False)  # already opened the loop
            slopes_plus = self.felix.get_slopes(n_ave=n_ave, remove_tilt=False)

            # Poke the other way and repeat
            a[i] = -1*poke
            self.apply_modes(a, basis, open=False)
            slopes_minus = self.felix.get_slopes(n_ave=n_ave, remove_tilt=False)
            
            imat[:,i] = slopes_plus - slopes_minus
            imat[:,i] /= 2*poke

        # Reset the DM to zero
        print_color("Reseting the actuators...", "cyan")
        self.rtc.poke_one_actuator(0, 0)
        
        cmat = np.linalg.pinv(imat)

        # Save the files
        date = get_timestamp(date_only=True)
        name_imat = f"imat.{date}.{name}"
        name_cmat = f"cmat.{date}.{name}"
        
        imat_path = os.path.join(SETTINGS["PATHS"]["felix"], name_imat + ".fits")
        print_color(f"Saving imat to {imat_path}", "cyan")
        hdu = fits.PrimaryHDU(imat)
        hdu.header["UTCTIME"] = get_timestamp()
        hdu.header["BASIS"] = basis
        hdu.header["N_MODES"] = n_modes
        hdu.header["UNITS"] = "Phase / actuator command"
        hdu.header["COMMENT"] = "Interaction matrix for FELIX. Phase is differential \
            slope measurement / subaperture width."
        hdu.writeto(imat_path, overwrite=True)

        cmat_path = os.path.join(SETTINGS["PATHS"]["felix"], name_cmat + ".fits")
        print_color(f"Saving imat to {cmat_path}", "cyan")
        hdu = fits.PrimaryHDU(cmat)
        hdu.header["UTCTIME"] = get_timestamp()
        hdu.header["BASIS"] = basis
        hdu.header["UNITS"] = "Inversion of imat - actuator command / phase"
        hdu.header["COMMENT"] = "Control matrix for FELIX"
        hdu.writeto(cmat_path, overwrite=True)
        
        if update:
            self.imat = imat
            self.cmat = cmat
            self.basis = basis
            self.a_prev = 0
        return cmat, imat
    
    def make_imat_empirical_slope_offsets(self, poke: float, n_ave: int, n_modes: int, update: bool = True, 
                                name: str = "felix") -> tuple[NDArray, NDArray]:
        """Creates a modal interaction matrix by injecting Zernikes onto the ASM
        and measuring the response of the WFS.

        Parameters
        ----------
        poke: float
            Poke command. Must be < 0.2 to avoid saturation.
        n_ave: int
            Number of frames to average per measurement.
        n_modes: int
            Number of modes.
        update: bool
            If True, updates the cmat used for the control loop.
        name: str
            Name of the imat and cmat.
        
        Returns
        -------
        imat: nd_array
            Interaction matrix.
        cmat: nd_array
            Control matrix, which is the (pseudo-) inverse of the imat.
        """
        assert np.abs(poke) < 0.5, "Poke amount must be less than 0.5"

        # Reset previous command as number of modes may have changed
        self.a_prev = np.zeros(n_modes)

        print_color("Starting imat. Make sure the imaka loop is closed.", "cyan")

        # Construct the interaction matrix. Dimensions are determined by number
        # of modes and number of slopes (spots * 2).
        imat = np.zeros((2 * SETTINGS["FELIX"]["n_spots"], n_modes))
        for i in range(n_modes):

            print_color("Poking mode " + str(i), "cyan")

            # + Poke
            a = np.zeros(n_modes)
            a[i] = poke
            self.rtc.load_slope_offsets(a)
            slopes_plus = self.felix.get_slopes(n_ave=n_ave, remove_tilt=False)

            # Poke the other way and repeat
            a[i] = -1*poke
            self.rtc.load_slope_offsets(a)
            slopes_minus = self.felix.get_slopes(n_ave=n_ave, remove_tilt=False)
            
            imat[:,i] = slopes_plus - slopes_minus
            imat[:,i] /= 2*poke

        # Reset to zero
        self.rtc.load_slope_offsets([0])
        
        cmat = np.linalg.pinv(imat)

        # Save the files
        date = get_timestamp(date_only=True)
        name_imat = f"imat.{date}.{name}"
        name_cmat = f"cmat.{date}.{name}"
        
        imat_path = os.path.join(SETTINGS["PATHS"]["felix"], name_imat + ".fits")
        print_color(f"Saving imat to {imat_path}", "cyan")
        hdu = fits.PrimaryHDU(imat)
        hdu.header["UTCTIME"] = get_timestamp()
        hdu.header["BASIS"] = "zernike"
        hdu.header["N_MODES"] = n_modes
        hdu.header["UNITS"] = "Phase / actuator command"
        hdu.header["COMMENT"] = "Interaction matrix for FELIX. Phase is differential \
            slope measurement / subaperture width."
        hdu.writeto(imat_path, overwrite=True)

        cmat_path = os.path.join(SETTINGS["PATHS"]["felix"], name_cmat + ".fits")
        print_color(f"Saving imat to {cmat_path}", "cyan")
        hdu = fits.PrimaryHDU(cmat)
        hdu.header["UTCTIME"] = get_timestamp()
        hdu.header["BASIS"] = "zernike"
        hdu.header["UNITS"] = "Inversion of imat - actuator command / phase"
        hdu.header["COMMENT"] = "Control matrix for FELIX"
        hdu.writeto(cmat_path, overwrite=True)
        
        if update:
            self.imat = imat
            self.cmat = cmat
            self.basis = "zernike"
            self.a_prev = 0
        return cmat, imat

    def _loop_iter(self, gain: float, leak: float, remove_tilt: bool = True) -> None:
        """Runs one iteration of the FELIX control loop.
        """
        #print(f"Previous input was {self.a_prev}")
        s = self.felix.get_slopes(remove_tilt=remove_tilt)
        a_now = np.dot(self.cmat, s)
        a = -1*gain*a_now + leak*self.a_prev
        #print(f"Current measurement is {a_now}")
        self.a_prev = a
        print_color("Settings modes: " + str(a), "cyan")

        # No need to open the loop for every single iteration
        self.apply_modes(a, basis=self.basis, open=False)
        self.loop_counter += 1

        self.tel_cmds.append(a)
        self.tel_slopes.append(s)
        self.tel_timestamps.append(self.felix.current_timestamp)
        
    def run_loop(self, gain: float, leak: float, remove_tilt: bool = True, n_iter: int = 10000000000) -> None:
        """Runs the loop for the specified number of iterations. This function runs
        one loop iteration and adds itself to the scheduler, allowing the loop to
        be run endlessly.

        Parameters
        ----------
        gain: float
            Loop gain.
        leak: float
            Loop leak.
        remove_tilt: bool, optional
            If True, subtracts the average spot position out of the slopes before
            generating commands. This effectively removes tip/tilt.
        n_iter: int, optional
            Number of iterations. Set to 1 million iterations by default, so
            this function will essentially run endlessly.

        Returns
        -------
        None
        """
        assert 0 <= gain <= 1, "gain must be between 0 and 1"
        assert 0 <= leak <= 1, "leak must be between 0 and 1"
        assert self.cmat is not None, "Control matrix must be defined"
        assert self.basis is not None, "Basis must be defined"

        # Make sure that the loop is open on the 'imaka RTC
        self.rtc.open_loop_noleak()
        # The timestep is defined by the frequency that FELIX outputs data
        for i in range(n_iter):
            self._loop_iter(gain, leak, remove_tilt)
            if self.loop_counter % 10 == 0:
                print_color(f"niter={self.loop_counter}", "cyan")

    def measure_cal_slopes(self, n_ave: int, cal_name: str | None = "cal") -> None:
        """Measures and sets calibration points.

        Parameters
        ----------
        n_ave: int
            Number of frames to average over.
        cal_name: str or None, optional
            File name to save to. If None, the file is not saved.
        """
        slopes = self.felix.get_slopes(n_ave=n_ave, remove_tilt=False)

        if cal_name is not None:
            date = get_timestamp(date_only=True)
            cal_path = os.path.join(SETTINGS["PATHS"]["felix"], cal_name + "." + date + ".fits")
            print_color(f"Saving calibration points to {cal_path}", "cyan")
            hdu = fits.PrimaryHDU(slopes)
            hdu.header["UTCTIME"] = get_timestamp()
            hdu.header["BASIS"] = self.basis
            hdu.header["COMMENT"] = "Calibration slopes for FELIX"
            hdu.writeto(cal_path, overwrite=True)

        self.felix.update_cal_slopes(slopes)

    def load_slope_offsets(self, a: ArrayLike) -> None:
        """Updates modal offsets.
    
        Parameters
        ----------
        a: array_like
            Modal coefficients.
        """
        assert self.basis is not None, "self.basis cannot be None. Did you set a cmat and imat?"
        # Check that the number of modes is okay
        mode2act = self.rtc.get_projection_matrix(self.basis)
        n_modes = mode2act.shape[1]
        assert len(a) <= n_modes, "Number of coefficients must be less than or equal \
            to number of modes defined in the z2a matrix" 
        
        slopes = np.dot(self.imat, a)
        self.felix.update_slope_offsets(slopes)

    def reset_all_slopes(self) -> None:
        """Resets all slope offsets and calibration slopes.
        """
        self.felix.update_cal_slopes(np.zeros_like(self.felix.cal_slopes))
        self.felix.update_slope_offsets(np.zeros_like(self.felix.slope_offsets))

    def set_flat_coeffs(self, a: ArrayLike) -> None:
        """Set flat commands in modal space. This can be used to set a static
        high order shape on the ASM.

        Parameters
        ----------
        a: array_like
            Modal coefficients.
        """
        assert self.basis is not None, "self.basis cannot be None. Did you set a cmat and imat?"
        if self.basis == "zernike":
            n_modes = self.rtc.z2a.shape[1] - 1  # includes piston (hypothetically)
        elif self.basis == "mirror":
            n_modes = self.rtc.mm2a.shape[1] - 1   # should also include piston...?
        else:
            raise ValueError("{self.basis} is not a recognized basis (\'zernike\' or \'mirror\'). " \
                             + "Check the cmat and imat headers.")
        
        self.a_flat = np.zeros(n_modes)
        self.a_flat[:len(a)] = a

    def apply_modes(self, a_in: ArrayLike, basis: str, open: bool = True) -> None:
        """Sends commands to the RTC for the specified modes. This is a wrapper
        for the function rtc.project_modes but allows us to add in additional
        high order modes before sending the command.

        The commands should not include piston.
        """
        if self.a_flat is None:
            coeffs = np.zeros(len(a_in) + 1)  # +1 to skip piston...
            coeffs[1:len(a_in)+1] = a_in

        else:
            # Use shape of flat commands
            coeffs = np.zeros(len(self.a_flat) + 1) 
            coeffs[1:len(a_in)+1] = a_in
            coeffs[1:] += self.a_flat

        self.rtc.project_modes(coeffs, basis=basis, open=open)

    def save_aocb(self, niter: int) -> None:
        """
        """
        for i in range(niter):
            pass