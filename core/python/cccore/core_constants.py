""" Core constants for the pipeline """
import os

USERNAME = os.environ["USERNAME"]
PYTHON_EXE = "C:/Python/python311/python.exe"
FFMPEG_EXE = "C:/ffmpeg/bin/ffmpeg.exe"

PROJECTS_DIR = "C:/Users/joele/Downloads/projects"

DEFAULT_FPS = "24"
FRAME_RATES = ["23.976", "24", "25", "29.97", "30"]

# project configurations
SERVER_PROJECT_CONFIG = "X:/Config_CC/projects_config.json"
LOCAL_PROJECT_CONFIG = f"{os.environ['USERPROFILE']}/Documents/projects_config.json"

PROGRESS_TEXT = "PROGRESS:"
MAXIMUM_VALUE_TEXT = "MAXIMUM VALUE:"

DEFAULT_START_FRAME = 1001
DEFAULT_END_FRAME = 1100
DEFAULT_HANDLES = 10
USERNAME = os.environ.get("USERNAME")


ASSET_STRUCTURE = "core/config/folder/asset_structure.yml"
SHOT_STRUCTURE = "core/config/folder/shot_structure.yml"
TASK_STRUCTURE = "core/config/folder/task_structure.yml"
