"""
AVGCS - Audio-Visual Game Control System

A Python module for real-time motion tracking and game control.
Supports both humanoid and non-humanoid character mapping.
"""

__version__ = "0.1.0"
__author__ = "Ashwath Narayanan"
__description__ = "Real-time motion tracking and game control system"

from .core import MotionTracker, PartMapper, MotionInterpreter
from .tracking import CameraTracker, MediaPipeTracker
from .mapping import CharacterMapper, MappingConfig
from .utils import load_config, save_config, validate_mapping, print_motion_data, print_game_commands

__all__ = [
    "MotionTracker",
    "PartMapper", 
    "MotionInterpreter",
    "CameraTracker",
    "MediaPipeTracker",
    "CharacterMapper",
    "MappingConfig",
    "load_config",
    "save_config",
    "validate_mapping",
    "print_motion_data",
    "print_game_commands"
] 