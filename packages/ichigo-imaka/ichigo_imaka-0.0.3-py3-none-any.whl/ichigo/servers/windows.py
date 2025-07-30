"""
TODO:
- maybe just listen to a socket and get rid of Pyro stuff?
"""

import os
import time
import numpy as np
import ichigo.images as images

from astropy.io import fits
from numpy.typing import NDArray
from ichigo.servers.server import Server
from ichigo.strmanip import print_color
from ichigo.config import SETTINGS

class WindowsNUCServer(Server):
    """Communicates with a Windows machine that hosts software for the camera
    and HASO WFS. The camera is controlled by SharpCap 4.0.
    """
    @staticmethod
    def _find_terminal_output(term_out: str, prefix: str) -> str:
        """Returns the output from the terminal filtered to locate the output
        path of files printed to the terminal.

        Parameters
        ----------
        term_out: str
            Output from the terminal.
        
        Returns
        -------
        out: str or None
            The filtered output.
        """
        lines = term_out.split('\n')  # split by newline
        for i, line in enumerate(lines):
            # Check each line and see which one contains the correct prefix. Can't
            # use str.startswith because the raw strings contain a ton of escape
            # characters.
            if prefix in line:
                # Split the string according to the prefix, but only get everything
                # after the prefix
                remote_out = line.split(prefix)[1]
                # If the last character is '\r', it means the string continued to
                # the next line.
                if remote_out.endswith('\r'):
                    # Remove \r from the end of the output
                    remote_out = remote_out[:-1]
                    # Get the next line
                    next_line = lines[i+1]
                    # Remove ANSI escape sequence - split this string by finding
                    # '\x1b', and taking all of the characters before that
                    remote_out += next_line.split('\x1b')[0]
                return remote_out
        raise ValueError("Could not find the output path of the saved image.")
    
    def __init__(self, alias: str, host_name: str | None = None, jumps: list[str] = []) -> None:
        """Initializes the WindowsNUCServer.

        Parameters
        ----------
        See ichigo.Server.__init__().

        Returns
        -------
        None
        """
        super().__init__(alias, host_name=host_name, os_type='windows', jumps=jumps)
        # Path to SharpCap scripts on the NUC
        self.path_sharpcap_scripts = "C:\\Users\\imaka\\Documents\\SharpCap\\scripts\\"
        self.path_waveview_scripts = "C:\\Users\\imaka\\Documents\\WaveView_auto\\scripts\\"
        self.path_spinview = "C:\\Users\\imaka\\Documents\\SpinView_auto\\"
        
        print_color("Created WindowsNUCServer. Please start SharpCap and the Pyro4 name server." \
              , "magenta")
    
    def spinview_capture_images(self, n: int, **kwargs) -> fits.HDUList:
        """Returns n images captured with SpinView.

        Parameters
        ----------
        n: int
            Number of images to capture.
        **kwargs:
            See capture_image.c.
        
        Returns
        -------
        out: fits.HDUList
            FITS data of the images.
        """
        raise NotImplementedError("SpinView capture is not implemented yet.")
        assert n / n == 1, "n must be an integer"
        assert n > 0, "n must be greater than 0"
        n = int(n)

        # Set remote absolute path for output file
        path_remote = self.path_spinview + "images\\temp.fits"
        # Make the commmand string
        cmd = self.path_spinview + "capture_image.exe"
        cmd += " -f " + path_remote
        cmd += " -n " + str(n)
        if len(kwargs) > 0:
            cmd += " --"
            for key, value in kwargs:
                cmd += " -c " + key + "=" + str(value)
        self.execute(cmd)

        path_local = os.path.join(SETTINGS["PATHS"]["temp"], "spinview.fits")
        self.sftp_get(path_remote, path_local)
        return fits.open(path_local)

    def sharpcap_get_camera_names(self) -> None:
        """Prints a list containing the names of all of the cameras connected to
        the SharpCap software. The output of this function can be used to determine
        which camera index to use. out[i] corresponds to index i when calling the
        function set_camera in this module.
        """
        # Format command for the python script
        cmd = "python " + self.path_sharpcap_scripts + "get_camera_names.py"
        self.execute(cmd)

    def sharpcap_set_camera(self, idx: int) -> None:
        """Sets the active camera. The output format is set to fits by default.
        Use the method sharpcap_set_output_format to change the format.

        This function calls the script set_camera.py.

        Parameters
        ----------
        idx: int
            Index of the camera. Use SharpCapServer.get_camera_names to find this,
            if need be. If idx == -1, the camera is closed.
        
        Returns
        -------
        None
        """
        # Format command for the python script
        cmd = "python " + self.path_sharpcap_scripts + "set_camera.py"
        # Add arguments
        cmd += " -i " + str(idx)
        self.execute(cmd)

    def sharpcap_set_output_format(self, format: str) -> None:
        """Sets the output format of saved files.

        This function calls the script set_output_format.py.

        Parameters
        ----------
        format: str
            Determines the output format of the files, which is fits by default.
            Set to fits, png, or tif.

        Returns
        -------
        None
        """
        # Format command for the python script
        cmd = "python " + self.path_sharpcap_scripts + "set_output_format.py"
        # Add arguments
        cmd += " -f " + str(format)
        self.execute(cmd)

    def sharpcap_capture_single_frame(self, fnout: str, t: float, g: float = 0) -> str:
        """Saves a single image and returns the absolute directory of the image.
        The image is saved to fnout in the directory PATH_SING_IMAGES.

        Parameters
        ----------
        fnout: str
            Name of the output file WITHOUT an extension. The extension will be
            appended automatically depending on the output format set. If you want
            to change to output format, use the method sharpcap_set_output_format().
        t: float
            Exposure time in milliseconds.
        g: float, optional
            The gain.

        Returns
        -------
        out: str
            Remote path to the saved image.
        """
        # Format command for the python script
        cmd = "python " + self.path_sharpcap_scripts + "capture_single_frame.py"
        # Add arguments
        cmd += " -fo " + fnout
        cmd += " -t " + str(t)
        cmd += " -g " + str(g)
        # Identify the output directory
        result = self.execute(cmd)
        fn_out = self._find_terminal_output(result, SETTINGS["WINDOWS"]["sharpcap_prefix"])
        return fn_out
        
    def sharpcap_capture_sequence(self, fout: str, n_frames: int, t: float, g: float = 0,
                                   fast: bool = True) -> None:
        """Saves a sequence of images. The image is saved under the folder fout
        in the directory PATH_SEQ_IMAGES.
        
        Unfortunately, it is difficult to get this function to return the remote
        directory of the saved images because of a bug in SharpCap's internal Python
        module.

        Parameters
        ----------
        fout: str
            Name of the output folder. Any spaces will be replaced by an underscore.
        n_frames: int
            Number of frames to capture.
        t: float
            Exposure time in milliseconds.
        g: float, optional
            The gain.
        fast: bool, optional
            If True, uses execute_fast to execute the command. I.e., do not wait
            for this sequence to finish before terminating this function.

        Returns
        -------
        None
        """
        # Format command for the python script
        cmd = "python " + self.path_sharpcap_scripts + "capture_sequence.py"
        # Add arguments
        cmd += " -fo " + fout.replace(' ', '_')
        cmd += " -n " + str(n_frames)
        cmd += " -t " + str(t)
        cmd += " -g " + str(g)
        if fast:
            self.execute_fast(cmd)
            print_color("Started sequence. Waiting a few seconds for it to go through...", "yellow")
            time.sleep(5)
        else:
            self.execute(cmd)
    
    def sharpcap_get_one_image(self, t: float, g: float = 0, n_ave: int = 1) -> NDArray:
        """Returns a single frame from the camera. This function runs the method
        sharpcap_capture_single_frame(), scps the file to a temporary directory
        on the machine running this package, and imports it to Python as a numpy
        array.

        The frames are averaged by capturing and transfering one image over time
        via SCP. If you don't need the result right now, it is faster to use
        sharpcap_capture_sequence() and retrieve the data yourself later.

        Parameters
        ----------
        t: float
            Exposure time in milliseconds.
        g: float, optional
            The gain.
        n_ave: int, optional
            Number of frames to average.

        Returns
        -------
        out: nd_array
            The most recent frame from the camera.
        """
        imgs = []
        for i in range(n_ave):
            path_remote = self.sharpcap_capture_single_frame("junk_sharpcap", t, g)
            # SFTP this file to the temporary directory
            fname = path_remote.split('\\')[-1]
            path_local = os.path.join(SETTINGS["PATHS"]["temp"], fname)
            self.sftp_get(path_remote, path_local)
            # Import this image as a numpy array
            img = images.get_image(path_local)
            imgs.append(img)
        
        imgs = np.array(imgs)
        output = np.mean(imgs, axis=0)
        return output
    
    def _run_waveview_task(self, script_name, wait, *args, **kwargs) -> str:
        """Runs a pyautogui task remotely. pyautogui requires the ability to take
        screenshots, which is usually not possible over SSH for security reasons.
        A workaround is to create a scheduled task, immediately run the task, and
        then delete it.
        """
        # Create the scheduled task. This is technically set to run every 10 hours,
        # but it doesn't matter because we are going to destroy the task as soon
        # as we run it.
        cmd = f"schtasks /create /sc HOURLY /mo 10 /tn ichigo_{script_name}" \
        + " /tr \"cmd /c start /min wscript //nologo " + self.path_waveview_scripts + "callpython.vbs " +  script_name + ".py "
        
        for arg in args:
            cmd += f"{arg} "
        for key, value in kwargs.items():
            # "store_true" arguments are passed without a value
            if value is True or value is False:
                if value:
                    cmd += f"-{key} "
            else:
                cmd += f"-{key} {value} "
        cmd += "\""
        self.execute(cmd)  # maybe I should check whether this hangs and reset scheduled tasks if it does
        # Run the task immediately. Use the powershell script to wait for the
        # task to finish...
        print_color("Attempting to run task...", "yellow")
        if wait:
            print_color("Waiting for task to finish...", "yellow")
            self.execute(f"powershell.exe {self.path_waveview_scripts}runschtask.ps1 ichigo_{script_name}")
        else:
            self.execute(f"schtasks /run /tn ichigo_{script_name}")
        # Delete the task
        self.execute(f"schtasks /delete /tn ichigo_{script_name} /f")

        # Print the stdout and stderr
        print_color("Finished task.", "green")
        result = self.execute("more " + self.path_waveview_scripts + "stdout.txt")
        return result
     
    def waveview_capture(self, folder_name: str, texpos: float, nave: int, nframes: int,
                         save_has: bool = True, force_same_folder: bool = False, wait: bool = False) -> None:
        """Saves wavefront data to the specified folder.

        NOTE: If background subtraction is enabled, the parameters texpos and
        nave will not be modified in WaveView. However, they are necessary to
        compute the time to wait between each capture.

        Parameters
        ----------
        folder_name: str
            Name of the output folder in the WaveView data directory.
        texpos: float
            Exposure time in milliseconds.
        nave: int
            Number of exposures to average per frame.
        nframes: int
            Number of frames to capture.
        save_has: bool, optional
            If True, the HAS data will be saved to the same folder with the same
            file names.
        force_same_folder: bool, optional
            If True, the data may be saved to a folder that already exists. If
            False, then if the folder already exists a suffix will be added to
            the folder name (e.g., my_folder_1).
        wait: bool, optional
            If True, wait for the task to finish before returning. If False,
            return immediately after starting the task.
        """
        assert type(folder_name) == str, "folder_name must be a string."
        assert len(folder_name) > 0, "folder_name must be a non-empty string."
        assert type(save_has) == bool, "save_has must be a boolean."

        self._run_waveview_task("capture_wavefront", wait, fn=folder_name, t=texpos, na=nave,
                                nf=nframes, sh=save_has, fsf=force_same_folder)  

    def waveview_get_data(self, folder_name: str, texpos: float, nave: int, nframes: int,
                          save_has: bool = True, force_same_folder: bool = False) -> NDArray:
        """Captures wavefront data and returns it as a numpy array. This is similar to waveview_capture(), but SFTPs the data to the local machine
        and returns it as a numpy array. The data is saved to the package temporary data directory.

        NOTE: If background subtraction is enabled, the parameters texpos and
        nave will not do anything.

        Parameters
        ----------
        See waveview_capture().
        """
        assert type(folder_name) == str, "folder_name must be a string."
        assert len(folder_name) > 0, "folder_name must be a non-empty string."
        assert type(save_has) == bool, "save_has must be a boolean."

        result = self._run_waveview_task("save_wavefront_as_fits", True, fn=folder_name, t=texpos, na=nave,
                                         nf=nframes, sh=save_has, fsf=force_same_folder)
        path_remote = self._find_terminal_output(result, SETTINGS["WINDOWS"]["waveview_prefix"])
        # SFTP this file to the temporary directory
        fname = "temp_"  + path_remote.split('\\')[-1]
        path_local = os.path.join(SETTINGS["PATHS"]["temp"], fname)
        self.sftp_get(path_remote, path_local)
        return fits.getdata(path_local)
    
    def reset_scheduled_tasks(self) -> None:
        """Removes all scheduled tasks that could have been created by ichigo.
        If the python script crashes and the task is not deleted, it will be
        impossible to create a new task with the same name. This function can be
        used to remove ichigo-generated tasks that were not properly deleted
        for some reason.
        """
        script_names = ["capture_wavefront", "save_wavefront_as_fits", "set_acquisition"]
        for script_name in script_names:
            self.execute(f"schtasks /delete /tn ichigo_{script_name} /f")