# ichigo

ichigo is a Python package for scripting the 'imaka RTC. It works by sending commands to different machines via SSH, which can be interacted with as Python classes or through a command line interface. ichigo was designed to communicate with the 'imaka RTC, IRTF ASM, and FELIX (facility WFS), but its core functionality can easily be repurposed for other AO systems.

### Directories

* ichigo: Package source code.
* docs: Package documentation.
* fnf: Fast and Furious for NCPA tuning. Originally written by Mike Bottom for Keck, but adapted here to work with ichigo.
* cameras: Scripts for operating Windows camera software through the command line.
* idl: Miscellaneous IDL scripts for the 'imaka RTC.