"""Contains server class for ehu.
"""

import os

from astropy.io import fits
from numpy.typing import NDArray
from ichigo.servers.imakartc import ImakaRTCServer
from ichigo.strmanip import print_color, get_timestamp, strip_ansi_codes
from ichigo.config import SETTINGS

class EhuServer(ImakaRTCServer):
    """Communicates with a helper server for the 'imaka RTC. The primary purpose
    of this server is to save AO telemetry.
    """
    def __init__(self, alias: str, host_name: str | None = None, jumps: list[str] = []) -> None:
        """Initializes the EhuServer object.

        Parameters
        ----------
        See :class:`ichigo.servers.server.Server`.

        Returns
        -------
        None
        """
        # Define additional files to source when running commands. This allows
        # us to use bin files like csclient, dsclient, and iload
        source = ["~/.bash_profile"]
        super().__init__(alias, host_name, jumps=jumps, source=source)
        # Set path for telemetry folders
        self.path_telemetry = '/data/asm/'
        
    def get_telemetry_path_today(self) -> str:
        """Returns the telemetry path for the current date. This is an absolute
        path on ehu.
        """
        utdate = get_timestamp(date_only=True)
        path_tel_today = self.path_telemetry + utdate + '/'
        return path_tel_today
    
    def get_aocb_path_today(self) -> str:
        """Returns the path for aocbs for the current date. This is an absolute
        path on ehu.
        """
        return self.get_telemetry_path_today() + 'ao/'
    
    def save_aocbs_autoidx(self, n_buffers: int) -> tuple[list[str], list[int]]:
        """Saves circular buffer telemetry with dsclient 12. This function automatically
        generates a folder on ehu for the UT date, if it doesn't exist yet, and
        also determines what the index of the file should be.
        
        Indexing starts at 0, so the first file saved will be aocb0000.fits.

        Parameters
        ----------
        fn: str
            Path to save the data to.
        n_buffers: int
            Number of circular buffers to save.
        
        Returns
        -------
        fnames_ehu: list of str
            Absolute paths to the telemetry files on ehu.
        indices: list of int
            aocb file name indices, e.g., aocb0002.fits corresponds to index 2.
        """
        assert isinstance(n_buffers, int), "n_buffers must be an integer"
        assert n_buffers > 0, "n_buffers must be greater than 0"
        
        # Make directory for the telemetry files, if it doesn't exist yet
        path_tel = self.get_aocb_path_today()
        self.execute("mkdir " + path_tel)

        # Get the current index. First get a list with all of the files in today's
        # telemetry directory
        print_color("Finding aocb files...", "yellow")
        result = self.execute("ls " + path_tel + " | grep aocb")
        result = result.replace('\n', '')  # remove newlines
        result = strip_ansi_codes(result).split('\r')  # remove ansi codes and split
        # Filter out the result to only include files with "aocb"
        result = [fn for fn in result if 'aocb' in fn]
        # If there are no telemetry files yet, set idx to 0
        print_color("Determining index...", "yellow")
        if len(result) == 0:
            idx = 0
        # Otherwise, figure out the next index from the filenames
        else:
            # Get the number from each filename and convert to a list of integers
            result = [fn.split('.fits')[0][4:] for fn in result]
            result = [int(num) for num in result]
            # Get the highest number. The new index will be the highest number + 1
            idx = max(result) + 1
            
        # Run dsclient an n_buffer number of times
        print_color("Saving " + str(n_buffers) + " telemetry files. Please wait...", "yellow")
        fnames_ehu = []
        indices = []
        for n in range(n_buffers):
            fname = path_tel + "aocb" + str(idx).zfill(4) + ".fits"
            fnames_ehu.append(fname)
            self.execute("dsclient 12 " + fname)
            indices.append(idx)
            idx += 1
            print_color("Done with " + str(n+1) + " of " + str(n_buffers), "yellow")
        
        return fnames_ehu, indices
    
    def get_aocbs_by_index(self, indices: list[int], date: None | str = None) -> tuple[list[fits.HDUList], list[str]]:
        """Returns aocb data for the current UT date. If the program is being
        run on ehu, this function will directly retrieve the data from the telemetry
        directory. If remote, then the files are SFTPed into a temporary directory
        on the local machine and are retrieved from there.

        Parameters
        ----------
        indices: list of int
            aocb file name indices, e.g., aocb0002.fits corresponds to index 2.
        date: str or None, optional
            Date of the telemetry data in the format 'YYYYMMDD'. If None, the
            current UT date is used.

        Returns
        -------
        aocb_data: list of astropy.io.fits.HDUList
            aocb data imported from FITS files.
        fnames_lcoal: list of str
            Path to file names on local machine.
        """
        if date:
            path_tel = self.path_telemetry + date + '/ao/'
        else:
            path_tel = self.get_aocb_path_today()
        # Absolute path to files on ehu
        fns_aocb_ehu = [path_tel + "aocb" + str(idx).zfill(4) + ".fits" for idx in indices]

        # If this function is not being run locally, SFTP files to local
        if self.is_remote():
            fnames_local = []
            # Index k starts from 0 and is meant for saving junk aocb files on
            # the local machine
            for k, fn_remote in enumerate(fns_aocb_ehu):
                basename = "junk_aocb" + str(k).zfill(4) + ".fits"
                fn_local = os.path.join(SETTINGS["PATHS"]["temp"], basename)
                self.sftp_get(fn_remote, fn_local)
                fnames_local.append(fn_local)
        # Otherwise, we're running this function on ehu. No need to SFTP files
        else:
            fnames_local = fns_aocb_ehu

        fits_data = []
        for fn in fnames_local:
            hdulist = fits.open(fn)
            fits_data.append(hdulist)

        return fits_data, fnames_local
    
    def get_imaka_data(self) -> fits.HDUList:
        """Saves an 'imaka telemetry file to the local machine.

        Parameters
        ----------
        None

        Returns
        -------
        out: fits.HDUList
            'imaka telemetry data.
        """
        # Make directory for junk (temporary) telemetry files on ehu
        path_tel = self.get_telemetry_path_today() + 'junk/'
        self.execute("mkdir " + path_tel)
        path_remote = path_tel + "junk_imaka_tel.fits"
        print_color("Requesting telemetry...", "yellow")
        self.execute("dsclient 7 " + path_remote)

        # SFTP the file to the local machine and read it in
        path_local = SETTINGS["RESOURCES"]["imaka_data"]
        self.sftp_get(path_remote, path_local)
        return fits.open(path_local)

    def get_average_actuator_cmd(self) -> NDArray:
        """Returns the average actuator commands over the number of loop iterations
        defined by the parameter nave in the 'imaka RTC. This does not include the
        flat commands.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Actuator commands are in extension 7
        imaka_data = self.get_imaka_data()
        return imaka_data[7].data[0]

    def set_open_loop_average(self, n_ave: int | None = None) -> None:
        """Opens the loop and sets commands to the average actuator command.
        """
        if n_ave is not None:
            self.execute(f"csclient set.nave {n_ave}")
        cmd = self.get_average_actuator_cmd()
        self.open_loop_noleak()
        self.set_actuator_commands(cmd)