""" Class to store values for the server and project specific"""
import os
import sys
import yaml
from typing import Optional


CONFIG_FMT = "{0}/core/config/project_config/{1}.yml"


class ReadData(object):
    """
    Read a yaml file and store the values in a dictionary
    """
    DEFAULT_PATH = None

    def __init__(self, read_path=None):
        # type: (Optional[str]) -> None
        """
        Args:
            read_path: Path of the yaml file to read
        """
        path = self.DEFAULT_PATH or read_path
        self.data = self.read_yaml(path)

    @staticmethod
    def read_yaml(path):
        """
        Read a yaml file and store the data

        Args:
            path: Path of the yaml to read

        Returns:
            data: The data of the yaml
        """
        with open(path) as file:
            data = yaml.safe_load(file)
        return data

    def get(self, key):
        # type: (str) -> Optional[dict]
        """
        Get the data

        Args:
            key: Key of data found

        Returns:
            data: The data dictionary
        """
        key_separated = key.split(".")
        data = self.data.copy()
        for v in key_separated:
            try:
                data = data[v]
            except KeyError:
                return dict()
        return data

    @staticmethod
    def join_list(*folder_args):
        # type: (list) -> str
        """
        Join a list of args to make a folder
        """
        args_list = list(folder_args)

        # convert list or tuple into folder list
        if isinstance(args_list[0], list):
            folder_list = args_list[0]
        else:
            folder_list = args_list

        # check all are valid string value
        if not all(isinstance(x, str) for x in folder_list):
            return str()

        # join values and clean path
        folder_path = os.path.join(*folder_list)
        folder_path_clean = str(folder_path).replace("\\", "/")
        return folder_path_clean


class ServerData(ReadData):
    """
    Server specific information
    """
    root_directory = os.path.dirname(__file__)
    DEFAULT_PATH = os.path.join(root_directory, "server.yml")

    def __init__(self, read_path=None):
        # type: (Optional[str]) -> None
        """
        Args:
            read_path: Path of the yaml file to read
        """
        super(ServerData, self).__init__(read_path)

        # ftrack variables
        self.api_key = self.data["api_key"]
        self.ftrack_url = self.data["ftrack_url"]
        self.api_user = self.data["api_user"]


class ProjectData(ServerData):
    """
    Project specific information rather
    than general server information
    """
    def __init__(self, project_name=None, *args, **kwargs):
        # type: (Optional[str], Optional[dict], Optional[dict]) -> None
        """
        Args:
            project_name: Name of the project to set
            *args: Additional args
            **kwargs: Optional args
        """
        super(ProjectData, self).__init__(*args, **kwargs)
        if project_name:
            os.environ["PROJECT_NAME"] = project_name

        self.project_name = os.environ.get("PROJECT_NAME")
        self.pipeline_type = os.environ.get("PIPELINE_TYPE")
        self.pipeline_root = os.environ.get("PIPELINE_ROOT")
        self.display_name = os.environ.get("DISPLAY_NAME")
        self.project_root = os.environ.get("PROJECT_ROOT")
        self.project_type = os.environ.get("PROJECT_TYPE")

    def get_custom_project_data(self):
        # type: () -> dict
        """
        Get any custom project data

        Returns:
            project_data: the custom project data if any
        """
        project_path = CONFIG_FMT.format(self.pipeline_root, self.project_name)
        if os.path.exists(project_path):
            project_data = self.read_yaml(project_path)
            return project_data
        return dict()

    @property
    def is_job(self):
        # type: () -> bool
        """ Is it a pitch project """
        if not self.project_name:
            return True
        return self.project_name[0].isdigit()

    def get_relative_path(self, file_name):
        # type: (str) -> str
        """
        Get the relative file path to the file name

        Args:
            file_name: Path to the file to find

        Returns:
            relative_path: Full path to the file
        """
        relative_path = f"{self.pipeline_root}/{file_name}"
        return relative_path

    def get_htoa_root(self, houdini_version):
        # type: (str) -> str
        """
        Get the root folder of the htoa plugin

        Args:
            houdini_version: The version of houdini to check against

        Returns:
            htoa_root: Root folder of the htoa
        """
        # add htoa variables
        htoa_mappings = self.get("htoa_mappings")
        htoa_folder = htoa_mappings[houdini_version]
        htoa_root = "/opt/Houdini/htoa/{htoa_folder}/{htoa_folder}".format(htoa_folder=htoa_folder)
        return htoa_root

    @property
    def maketx(self):
        # type: () -> str
        """
        The make tx file path
        """
        houdini_version = os.environ.get("APP_VERSION")
        htoa_mappings = self.get("htoa_mappings")

        # if not version given or the version is not
        # in the mapping default to the latest
        if not houdini_version or houdini_version not in htoa_mappings:
            houdini_version = list(htoa_mappings.keys())[-1]

        htoa_root = self.get_htoa_root(houdini_version)
        maketx = f"{htoa_root}/scripts/bin/maketx"
        return maketx

    @property
    def sequence_folders(self):
        # type: () -> list[str]
        """ Get a list of sequence folders """
        folders = os.listdir(self.vfx_root)
        sequence_folders = [folder for folder in folders if folder[0].isupper()]
        sequence_folders.sort()
        return sequence_folders

    def get_shot_folders(self, sequence_name):
        # type: (str) -> list[str]
        """
        Get a list of shot folders from a sequence

        Args:
            sequence_name: The sequence name to find

        Returns:
            shot_folders: List of shot folders
        """
        sequence_root = os.path.join(self.vfx_root, sequence_name)
        folders = os.listdir(sequence_root)
        shot_folders = [folder for folder in folders if folder[0].isalnum()]
        shot_folders.sort()
        return shot_folders

    @property
    def is_super_user(self):
        # type: () -> bool
        """ Is the current artist a super user """
        super_user = self.get("super_user")
        current_user = os.environ.get("USER")
        return current_user in super_user
