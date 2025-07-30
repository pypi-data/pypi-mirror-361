"""Command line interfaces for running ichigo.
"""

import os
import readline
import traceback
import ichigo.scripting.obsscripts as obsscripts
import ichigo.scripting.pyscripts as pyscripts

from importlib import reload
from ichigo.strmanip import print_color, print_line
from ichigo.managers import ScriptManager, StateManager, FELIXLoopManager
from ichigo.servers import *
from ichigo.config import SETTINGS


def script_cli() -> None:
    """Interface for basic script execution.
    """
    print("Initializing...")
    # Import hosts that are enabled in hosts.json
    manager = ScriptManager()
    manager.import_enabled_hosts()
    scripts_folder = SETTINGS["PATHS"]["txtscripts"]

    # Check whether IDL is enabled as this may cause weird interactions with the
    # CLI upon initialization
    if SETTINGS["IDL"]["enable_idl"]:
        print_color("WARNING: The Python to IDL bridge is enabled. It may cause strange" + \
                    " behavior in the CLI.", "red")
        input("Press Enter to continue...\n")

    # Ask if the user is ready to connect
    while True:
        response = input("Ready to connect? (y/n): ")
        match response.lower():
            case "y":
                # Exit the while loop
                break
            case "n":
                # Terminate the program
                print("Exiting.")
                return
            case _:
                # Unrecognized response, try again
                print("Response not recognized. Please try again.")

    # Now connect and begin executing scripts. Use a finally block to make sure
    # that we always disconnect if something goes wrong
    try:
        print_color("Connecting...", "yellow")
        manager.connect_all()
        print_color("Connected successfully. Please check that asmports and the loop are running.\n", "green")

        # Ask for observing scripts repeatedly until the user quits the program
        while True:
            response = input("What would you like to do?\n" \
                            + "  [0] Execute a single line. \n"
                            + "  [1] Execute a TXT script.\n" \
                            + "  [2] List available scripts.\n" \
                            + "  [q] Quit.\n" \
                            + ">>> ")
            print('')
            match response:
                case "0":
                    # Keep asking for lines until the user stops
                    flag = True
                    while flag:
                        line = input("Enter one line that follows the syntax of an observing script."
                                     + "\n(\"q\" to quit; \"r\" to refresh python scripts.)\n>>> ")
                        if line == "q":
                            # Exit the while loop
                            flag = False
                            print('')
                            continue
                        if line == "r":
                            # Refresh python scripts
                            print("Reloading module pyscripts...")
                            reload(pyscripts)
                            print("Done\n")
                            continue
                        print_line()
                        try:
                            manager.execute_line(line)
                        except:
                            print_color("Line execution failed!", "red")
                            traceback.print_exc()
                        print_line()  
                case "1":
                    script_name = input("Enter the file name of a script.\n>>> ")
                    # Throw it out if it isn't a txt file
                    if not script_name.lower().endswith(".txt"):
                        script_name += ".txt"
                    # First, check if it's in the observing scripts directory
                    script_path = obsscripts.get_script_abspath(script_name)
                    if not os.path.isfile(script_path):
                        print("This doesn't exist in the observing scripts directory:\n" \
                              + "  " + scripts_folder)
                        print("Attempting to load as an absolute path...")
                        script_path = script_name
                        if not os.path.isfile(script_path):
                            print_color("This file doesn't seem to exist. Please try again.\n", "yellow")
                            # Go back to beginning
                            continue
                    # If we were able to successfully find the TXT file, attempt to
                    # execute it
                    print_line()

                    # On rare occasions the connection to the server may suddenly
                    # terminate. If this happens, attempt to reconnect with a while
                    # loop. If the script fails for unrelated reasons or succeeds
                    # then break out of the loop.
                    k = 1
                    kmax = 6
                    while k < kmax:
                        try:
                            manager.execute_obs_script(script_path)
                            break
                        except paramiko.SSHException:
                            print_color(f"Connection lost. Attempt to reconnect {k} of {kmax-1}...", "red")
                            manager.connect_all()
                            k += 1
                        except:
                            print_color("Script execution failed!", "red")
                            traceback.print_exc()
                            break
                    print_line()
                    print('')

                case "2":
                    print("TXT files in the observing scripts directory: ")
                    print("  " + scripts_folder)
                    for fn in os.listdir(scripts_folder):
                        print("    " + fn)
                    print("Python functions defined in module pyscripts: ")
                    for func_name in obsscripts.get_py_scripts():
                        print("    " + func_name)
                    print('')
                case "q":
                    # Go to finally block
                    return
                case _:
                    # Unrecognized response, try again
                    print("Response not recognized. Please try again.\n")
    finally:
        manager.disconnect_all()
        print_color("All servers have been disconnected. Goodbye!", "green")
        # <3 <3 <3
        print(8 * '\033[31m<3\033[0m\033[36m<3\033[0m\033[33m<3\033[0m' + '\n')


def overseer_cli(t_update: float | None = None) -> None:
    """Interface for the overseer, which offloads tip/tilt to the telescope and
    monitors DM saturation. [supposedly]
    """
    # Use ehu to get the zernikes and max to communicate with the TCS. 
    # Create a manager that will automatically check the state of the system.
    if t_update is None:
        t_update = -1

    manager = StateManager(t_update=t_update)
    ehu = manager.servers_dict["ehu"]

    try:
        print_color("Connecting...", "yellow")
        manager.connect_all()

        if t_update != -1:
            manager.run()

        else:
            while True:
                response = input("Enter to check state, or \"q\" to quit: ")
                if response == "q":
                    return
                else:
                    manager.check_state()

    finally:
        manager.disconnect_all()
        print_color("All servers have been disconnected. Goodbye!", "green")
        # <3 <3 <3
        print(8 * '\033[31m<3\033[0m\033[36m<3\033[0m\033[33m<3\033[0m' + '\n')
