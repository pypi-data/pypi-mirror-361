# FILE: config.py
# Contains default configuration values and path
# Note: The files are assumed to be in data/.

# Import packages
from dataclasses import dataclass, field

from ichigo.config import SETTINGS

@dataclass
class CacofoniConfig:
    telemetry_filename: str = "aocb0090.fits"
    param_filename: str = SETTINGS["RESOURCES"]["imaka_parm"]  # imakaparm.txt
    modal_filename: str = SETTINGS["RESOURCES"]["mm2a"] #"mm2a_norm.fits"
    
    minimum_freq_hz: float = 4.0
    maximum_freq_hz: float = 10.0
    
    n_actuators: int = SETTINGS["AO"]["n_actuators"]
    n_xsubapertures: int = int( SETTINGS["AO"]["n_subaps"]**0.5 )
    n_ysubapertures: int = int( SETTINGS["AO"]["n_subaps"]**0.5 )
    
    closed: bool = False
    modal: bool = False
    thresh: bool = None
    apply_hanning: bool = False
    laplacian: bool = True
    silent: bool = False
    
def print_config(config):
    print(f"[Config] Assuming {config.n_actuators} actuators from config for loading telemetry data.")
    print(f"[Config] Assuming {config.n_xsubapertures} 'x' subapertures from config for loading telemetry data.")
    print(f"[Config] Assuming {config.n_ysubapertures} 'y' subapertures from config for loading telemetry data.\n")
    print(f"[Config] Assuming {config.minimum_freq_hz} Hz for minimum frequency.")
    print(f"[Config] Assuming {config.maximum_freq_hz} Hz for maximum frequency.\n")
    
    return