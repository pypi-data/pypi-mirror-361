"""
TODO:
- run on ehu
"""

import argparse

from ichigo.ui.cli import *


if __name__ == '__main__':
    # Create parser for command line arguments
    parser = argparse.ArgumentParser(
        prog="ichigo",
        description="Package for scripting the 'imaka RTC."
        )
    parser.add_argument("--mode", type=str, help="Usage mode.")
    parser.add_argument("-t", "--t_update", type=float, default=None, help="Time between overseer updates in seconds.")
    args = parser.parse_args()
    if not args.mode:
        # Open the command line interface for running scripts
        script_cli()
    else:
        match args.mode:
            case "overseer":
                overseer_cli(args.t_update)
            case _:
                print("Usage mode not recognized.")