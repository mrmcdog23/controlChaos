""" Core constants for the pipeline """
import os
from enum import Enum


PYTHON_EXE = "C:/Python/python311/python.exe"
FFMPEG_EXE = "C:/ffmpeg/bin/ffmpeg.exe"

PROJECTS_DIR = "C:/Users/joele/Downloads/projects"

DEFAULT_FPS = "24"
FRAME_RATES = ["23.976", "24", "25", "29.97", "30"]


class APPS(Enum):
    HOUDINI = ["21.0.512", "20.5.445", "20.0.590"]
    NUKE = ["16.0v6", "16.0v4"]
    MAYA = ["2027", "2026", "2025", "2024", "2023"]
    UNREAL = ["5.8", "5.7", "5.6", "5.5"]


# project configurations
SERVER_PROJECT_CONFIG = "X:/Config_CC/projects_config.json"
LOCAL_PROJECT_CONFIG = f"{os.environ['USERPROFILE']}/Documents/projects_config.json"
