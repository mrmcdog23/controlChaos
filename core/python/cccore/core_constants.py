""" Core constants for the pipeline """
import os
from enum import Enum


PYTHON_EXE = "C:/Python/python311/python.exe"
FFMPEG_EXE = "C:/ffmpeg/bin/ffmpeg.exe"

PROJECTS_DIR = "C:/Users/joele/Downloads/projects"

DEFAULT_FPS = "24"
FRAME_RATES = ["23.976", "24", "25", "29.97", "30"]

# project configurations
SERVER_PROJECT_CONFIG = "X:/Config_CC/projects_config.json"
LOCAL_PROJECT_CONFIG = f"{os.environ['USERPROFILE']}/Documents/projects_config.json"
