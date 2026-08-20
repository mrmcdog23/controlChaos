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

        # add server prefix if on a mac
        self.server_prefix = self.data["win_server_prefix"]
        self.jobs_dir = self.data["win_jobs_dir"]
        self.pitch_dir = self.data["win_pitch_dir"]
        self.masters_dir = self.data["masters_dir"]


        # pipeline variables
        self.code_root = self.server_prefix + self.data["code_root"]
        self.branch_root = self.server_prefix + self.data["branch_root"]
        self.beta_root = self.server_prefix + self.data["beta_root"]
        self.stable_root = self.server_prefix + self.data["stable_root"]
        self.project_database_path = self.server_prefix + self.data["project_database_path"]

        # temporary data paths
        self.backup_dir = self.server_prefix + self.data["backup_dir"]
        self.artist_scripts = self.data["artist_scripts"]
        self.artist_data = self.server_prefix + self.data["artist_data"]
        self.flame_data = self.data["flame_data"]
        self.thumbnail_dir = self.data["thumbnail_dir"]

        # git relative variables
        self.git_source = self.data["git_source"]
        self.git_url = self.data["git_url"]

        # ftrack variables
        self.ftrack_server = self.data["ftrack_server"]
        self.api_key = self.data["api_key"]
        self.server_url = self.data["server_url"]

        # deadline variables
        self.deadline_dir = self.data["deadline_dir"]
        self.deadline_data = self.server_prefix + self.data["deadline_data"]
        self.deadline_user_data_path = self.data["deadline_user_data_path"]
        self.farmer_freds_url = self.data["farmer_freds_url"]

        # frameio variables
        self.frameio_url = self.data["frameio_url"]
        self.frameio_token = self.data["frameio_token"]
        self.frameio_team_id = self.data["frameio_team_id"]

        # nuke variables
        self.third_party_nuke_dir = self.data["third_party_nuke_dir"]
        self.share_nodes_dir = self.data["share_nodes_dir"]
        self.foundry_licence = self.data["foundry_licence"]
        self.shared_gizmo_dir = self.server_prefix + self.data["shared_gizmo_dir"]
        self.optical_flares_licence_path = self.data["optical_flares_licence_path"]
        self.optical_flares_licence_preset = self.data["optical_flares_licence_preset"]

        # houdini variables
        self.third_party_houdini_dir = self.data["third_party_houdini_dir"]
        self.houdini_template_dir = self.data["houdini_template_dir"]
        self.shared_otls_dir = self.data["shared_otls_dir"]

        # mayas paths
        self.maya_third_party_dir = self.data["maya_third_party_dir"]

        # media shuttle variables
        self.media_shuttle_dir = self.data["media_shuttle_dir"]

        # flame variables
        self.default_flame_project_root = self.data["default_flame_project_root"]

        # maya plugins
        self.animbot_config_path = self.data["animbot_config_path"]

        # mac jobs directory
        self.mac_jobs_dir = self.data["mac_jobs_dir"]


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

        # work out the mount directory
        if not self.is_job:
            self.jobs_dir = self.pitch_dir

        # check for a custom project root and if there is one override the default
        custom_project_data = self.get_custom_project_data()
        job_dir_key = "mac_jobs_dir" if sys.platform == "darwin" else "jobs_dir"
        custom_jobs_dir = custom_project_data.get(job_dir_key)
        if custom_jobs_dir:
            self.jobs_dir = custom_jobs_dir

        # set the mac directory
        self.mac_jobs_dir = custom_project_data.get("mac_jobs_dir", self.mac_jobs_dir)

        # set the project root
        self.project_root = self.join_list(self.jobs_dir, self.project_name)
        os.environ["PROJECT_ROOT"] = self.project_root

        self.vfx_root = self.join_list(self.project_root, "vfx")
        self.icon_dir = self.join_list(self.pipeline_root, "core", "icons")
        self.appdata = self.join_list(self.vfx_root, "appdata")
        self.is_development = self.pipeline_type == "Development"
        self.is_longform = self.project_type == "longform"
        self.is_commercial = self.project_type == "commercial"

        # set the correct ocio file
        if self.is_commercial:
            self.ocio_path = self.data["commercials_ocio_path"]
        else:
            self.ocio_path = self.data["longform_ocio_path"]

        # project appdata directories
        self.ingested_tracking_dir = self.join_list(self.appdata, "ingested_tracking")

        # houdini root directories
        self.houdini_root = self.join_list(self.vfx_root, "tools", "houdini")
        self.project_otls_dir = self.join_list(self.houdini_root, "otls")
        self.project_shelves_dir = self.join_list(self.houdini_root, "shelves")

        # default config path
        defaults_path = CONFIG_FMT.format(self.pipeline_root, "defaults")
        defaults_data = self.read_yaml(defaults_path)
        self.data.update(defaults_data)

        # project config path
        custom_project_data = self.get_custom_project_data()
        self.data.update(custom_project_data)

        # set the correct ocio file
        if self.is_commercial:
            self.shot_extract_regex_list = self.data["commercials_shot_regex_list"]
        else:
            self.shot_extract_regex_list = self.data["longform_shot_regex_list"]
        self.ingest_component_names = self.data["ingest_component_names"]

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
