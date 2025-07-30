"""Contains server class for the imaka RTC.
"""

import time
import sched
import numpy as np

from astropy.io import fits
from numpy.typing import NDArray, ArrayLike
from ichigo.servers.server import Server
from ichigo.strmanip import print_color
from ichigo.config import SETTINGS


class ImakaRTCServer(Server):
    """Communicates with the real time controller. This includes sending actuator
    commands, changing loop parameters, and retrieving telemetry.

    This object is currently configured for the 'imaka RTC! This means that any
    shell functions are hard-coded. Several attributes are also hard-coded in
    __init__(), although they can easily be changed.
    """
    def __init__(self, alias: str, host_name: str | None = None, jumps: list[str] = []
                 , source: list[str] | None = None) -> None:
        """Initializes the RTCServer object.

        Parameters
        ----------
        name
            See :py:class:`~sservers.network.Server`
        """
        # Define additional files to source when running commands. This allows
        # us to use bin files like csclient, dsclient, and iload
        source_rtc = ["/home/imaka/.profile"]
        # Override this value if specified
        if source:
            source_rtc = source
        super().__init__(alias, host_name, jumps=jumps, source=source_rtc)

        # Calibration files - include '/' at the end
        self.cals_path = "/home/imaka/cals/"

        # Retrieve data files
        self.z2a = fits.getdata(SETTINGS["RESOURCES"]["z2a"], ext=0)
        self.a2z = fits.getdata(SETTINGS["RESOURCES"]["a2z"], ext=0)
        self.zer_to_slopes = fits.getdata(SETTINGS["RESOURCES"]["z2slopes"], ext=0)
        self.mm2a = fits.getdata(SETTINGS["RESOURCES"]["mm2a"], ext=0)
        # Keep current slope offsets - this is necessary for Fast and Furious.
        # IF SOMEBODY SETS SLOPE OFFSETS OUTSIDE OF THIS PROGRAM IT WILL BE STALE!
        self.zern_offsets = np.zeros(self.zer_to_slopes.shape[1])

    def panic(self) -> None:
        """Opens the loop and leaks off excess voltages. Use this function as a
        panic button to protect the DM if the system enters an undesirable state.
        """
        print_color("PANIC: Opening the loop!", "red")
        self.execute("csclient set.dmservo.type 1")  # PID controller
        self.execute("csclient loop.gain 0")         # gain to 0
        self.execute("csclient loop.gain.pb 0")      # playback gain to 0
        print_color("PANIC: Leaking off commands. Please wait...", "red")
        self.execute("csclient loop.gain.int 0.98")  # leak to 0.98
        time.sleep(3)  # sleep for a little bit so everything can leak off
        self.execute("csclient loop.gain.int 1")
        print_color("Finished panicking. Please check the state of the loop!", "red")

    def make_start_loop_cmd(self) -> str:
        """Returns the command needed to start the loop with the imat, cmats, and
        playback buffer specified when initializing the RTCServer object. This
        is needed to load the correct cmats when scripting observing sequences.

        Parameters
        ----------
        None

        Returns
        -------
        out: str
            Shell command to start the loop.
        """
        raise NotImplementedError("This method is not implemented yet.")
        cmd = "loop "
        return cmd
    
    def set_loop_pid(self, gain: float, leak: float, pbgain: float) -> None:
        """Sets PID loop parameters. The parameters are set in this order:
        leak -> gain -> pbgain.

        Parameters
        ----------
        gain: float
            PID gain, 0 <= gain <= 0.5.
        leak: float
            PID leak, 0.9 <= leak <= 1.
        pbgain: float
            Playback buffer gain, 0 <= pbgain <= 0.1.

        Returns
        -------
        None
        """
        assert 0 <= gain <= 0.5, "PID gain must be between 0 and 0.5"
        assert 0.9 <= leak <= 1, "PID leak must be between 0.9 and 1"
        assert 0 <= pbgain <= 1, "pbgain must be between 0 and 1"
            
        self.execute("csclient set.dmservo.type 1")
        self.execute("csclient loop.gain.int " + str(leak))
        self.execute("csclient loop.gain " + str(gain))
        self.execute("csclient loop.gain.pb " + str(pbgain))
    
    def open_loop_noleak(self) -> None:
        """Opens the loop.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        print_color("Opening the loop.", "yellow")
        self.set_loop_pid(gain=0, leak=1, pbgain=0)

    def set_actuator_commands(self, c: NDArray) -> None:
        """Sends actuator commands.

        Parameters
        ----------
        c: nd_array of size n_actuators OR n_channels
            Commands to send to the actuators, where n_actuators is the number of
            actuators and n_channels is the number of channels.
        
        Returns
        -------
        None
        """
        n_act = SETTINGS["AO"]["n_actuators"]
        n_channels = SETTINGS["AO"]["n_channels"]
        assert (len(c)==n_act or len(c)==n_channels), "The number of commands \
            must be equal to the number of actuators OR the number of channels."
        assert np.max(np.abs(c)) <= 0.4, "Actuator command cannot exceed 0.4."
        
        # If the number of commands is less than the number of channels, pad
        # with zeros
        if len(c) != n_channels:
            c_chan = np.zeros(n_channels)
            c_chan[:len(c)] = c
        # Otherwise, the number of commands must equal the number of channels.
        # No padding necessary
        else:
            c_chan = np.array(c)
        # Generate the command string
        c_str = "csclient set.act.volts "
        for num in c_chan:
            c_str += '{:.6f}'.format(num) + ' '
        # Send the command to the RTC
        print_color("Setting actuators: " + c_str, "yellow")
        self.execute(c_str)

    def poke_one_actuator(self, idx: int, amp: float) -> None:
        """Pokes one actuator by a specified amplitude.

        Parameters
        ----------
        idx: int or list
            Actuator index.
        amp: float
            Amplitude of the poke in normalized actuator command.
        
        Returns
        -------
        None
        """
        n_actuators = SETTINGS["AO"]["n_actuators"]
        # Create an array of zeros, then set the value of the array at the
        # specified index
        c_act = np.zeros(n_actuators)
        c_act[idx] = amp
        self.set_actuator_commands(c_act)

    def get_flat_cmd(self) -> NDArray:
        """Returns flat commands stored on the local machine. If you need to update
        the flat commands, run scripting.pyscripts.update_dmflat().

        Parameters
        ----------
        None

        Returns
        -------
        out: nd_array of size n_channels
            Averaged actuator commands that are sent to the RTC.
        """
        return fits.getdata(SETTINGS["RESOURCES"]["dm_flat"])
    
    def get_projection_matrix(self, basis: str) -> NDArray:
        """Returns the projection matrix for a given basis set.

        Parameters
        ----------
        basis: str
            Basis set of modes to use. Choose from one of the following:
                zernike: Noll Zernike polynomials.
                mirror: Mirror modes generated by Olivier Lai.

        Returns
        -------g
        out: nd_array of size (n_actuators, n_modes)
            A projection matrix that converts modes to actuators.
        """
        matrix_dict = {
            "zernike": self.z2a,
            "mirror": self.mm2a
        }
        return matrix_dict[basis]
        
    def project_modes(self, a: ArrayLike, basis: str, open: bool = True) -> NDArray:
        """Projects a mode onto the DM. Used as a template for the methods
        project_zernikes() and project_mirror_modes().

        Parameters
        ---------
        a: array_like
            Coefficients of the basis set to project onto the DM. Limits to the
            length of this array depend on the basis.
        basis: str
            See the method get_projection_matrix().
        open: bool, optional
            If True, opens the loop before sending the commands.
        add_flat: bool, optional
            If True, adds stored average commands to the DM.
        
        Returns
        -------
        c: nd_array of size n_channels
            Actuator commands projected on the mirror.
        """
        mode2act = self.get_projection_matrix(basis)
        # Check the size of the array to see if it matches the number of modes
        # defined in the conversion matrix
        n_modes = mode2act.shape[1]
        assert len(a) <= n_modes, "Number of coefficients must be less than or equal \
            to number of modes defined in conversion matrix (e.g., z2a)"
        a = np.array(a)
        
        n_act = SETTINGS["AO"]["n_actuators"]
        # Pad the array if necessary
        if len(a) < n_modes:
            a_pad = np.zeros(n_modes)
            a_pad[:len(a)] = a
            a = a_pad
        # Convert coefficients to actuator commands
        c = np.zeros(64)
        c[:n_act] = np.dot(mode2act, a)

        if open:
            self.open_loop_noleak()
        self.set_actuator_commands(c)
        return c

    def project_zernikes(self, a_z: ArrayLike, open: bool = True) -> NDArray:
        """Projects Zernike modes onto the DM.

        Parameters
        ---------
        See project_modes().

        Returns
        -------
        c: nd_array of size n_channels
            Actuator commands projected on the mirror.
        """
        return self.project_modes(a_z, basis="zernike", open=open)
   
    def project_mirror_modes(self, a_m: ArrayLike, open: bool = True) -> NDArray:
        """Projects mirror modes onto the DM.

        Parameters
        ---------
        See project_modes().

        Returns
        -------
        c: nd_array of size n_channels
            Actuator commands projected on the mirror.
        """
        return self.project_modes(a_m, basis="mirror", open=open)
    
    def set_slope_offsets(self, slopes: NDArray, wfs: int = 0) -> None:
        """Sets slope offsets manually.

        Parameters
        ----------
        slopes: array_like
            Slope offsets to set. Length must be equal to 2 times the total number
            of subapertures.
        wfs: int, optional
            Index of the wavefront sensor.

        Returns
        -------
        None
        """
        assert len(slopes) == 2 * SETTINGS["AO"]["n_subaps"], "slopes must be of length 2 * n_subaps."

        cmd = f"csclient set.slope.offsets \"ichigo_offset\" {wfs} "
        for s in slopes:
            cmd += '{:.4f}'.format(s) + ' '
        self.execute(cmd)

    def load_slope_offsets(self, a_z: ArrayLike | int, wfs: int = 0) -> None:
        """Loads Zernike slope offsets into the RTC. The slope offsets are computed
        by doing the dot product [zer_to_slopes][a_z].

        Parameters
        ----------
        a_z: array_like
            Zernike coefficients for the slope offsets, WITHOUT piston. The
            dimensions of a_z must match zer-to-slopes.fits.
        wfs: int, optional
            Index of the wavefront sensor.

        Returns
        -------
        None
        """
        assert len(a_z) <= self.zer_to_slopes.shape[1], "Dimensions of a_z must" \
            + " be less than or equal to the number of Zernike coefficients in z2slopes" \
            + " defined in settings.ini"
        
        a_z_padded = np.zeros(self.zer_to_slopes.shape[1])
        a_z_padded[:len(a_z)] = a_z
        self.zern_offsets = a_z
        offsets = np.dot(self.zer_to_slopes, a_z_padded)
        
        print_color("Sending Zernike offsets: " + str(self.zern_offsets), "yellow")
        self.set_slope_offsets(offsets, wfs)

    def chop(self, a_ra: float, a_dec: float, f: float, n_iter: int) -> None:
        """Opens the loop and the ASM for a certain number of iterations.

        Parameters
        ----------
        a_ra: float
            Amplitude in RA in arcseconds.
        a_dec: float
            Amplitude in Dec in arcseconds.
        f: float
            Chop frequency in Hz.
        n_iter: int
            Number of iterations to chop.

        Returns
        -------
        None
        """
        assert f < 5, "Chop frequency must be less than 5 Hz."
        assert f > 0.01, "Chop frequency must be greater than 0.01 Hz."

        m = SETTINGS["AO"]["RADec_to_NollSurface"]
        # Amplitudes in terms of tip/tilt Zernike coefficients
        a2, a3 = np.dot(m, [a_ra, a_dec])

        self.open_loop_noleak()
        # Time between each chop in seconds
        dt = 1/f
        t = 0.
        scheduler = sched.scheduler(time.time, time.sleep)

        for i in range(n_iter):
            # Chop - loop is already open, set open=False
            scheduler.enter(t, 1, self.project_zernikes, ([a2, a3], False,))
            t += dt/2
            # Go back to initial position
            scheduler.enter(t, 1, self.project_zernikes, ([0], False,))
            t += dt/2
        scheduler.run()