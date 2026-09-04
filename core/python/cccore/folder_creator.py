""" Class to create folder structure on a project """
import os
from typing import Optional
import cccore.utils.file_utils as file_utils
import cccore.data.server_data as server_data
import cccore.utils.cc_logging as cc_logging
import cccore.core_constants as core_constants


class CreateFolders(object):
    """
    Create the folders on disk on a project
    """
    def __init__(self, project_name=None):
        # type: (Optional[str]) -> None
        """
        Args:
            project_name: Name of the project to set to
        """
        super().__init__()
        self.data = server_data.ProjectData(project_name=project_name)
        self.logger = cc_logging.cc_logger()
        self.logger.disabled = True

        # initialise class variables
        self.project_name = project_name
        self.folder_structure = dict()
        self.create_dict = dict()
        self.project_root = str()

    def load_structure(self, structure):
        # type: (str) -> dict
        """
        Load the folder structure from the relevant yaml

        Args:
            structure: Path of the structure yaml file
        """
        folder_structure_path = self.data.get_relative_path(structure)
        return file_utils.read_file(folder_structure_path)

    def reset_project_data(self, project_name):
        # type: (str) -> None
        """
        Reset the data variable to the default

        Args:
            project_name: Project name to set to
        """
        self.data = server_data.ProjectData(project_name)

    @staticmethod
    def create_folders_from_list(parent_dir, folder_list):
        # type: (str, list[str]) -> None
        """
        Create a list of folders under a given directory

        Args:
            parent_dir: Path to the parent directory
            folder_list: List of folder names to create
        """
        for sub_name in folder_list:
            sub_dir = os.path.join(parent_dir, sub_name)
            file_utils.create_directory(sub_dir)

    def iteritems_recursive(self, d):
        # type: (dict) -> (set, str)
        """
        Recursively build folder path

        Args:
            d: Dictionary of folder structure

        Returns:
            Folder set
            Folder name
        """
        for k, v in d.items():
            if isinstance(v, dict):
                for k1, v1 in self.iteritems_recursive(v):
                    yield (k,) + k1, v1
            else:
                yield (k,), v

    def create_project_structure(self, project_root):
        # type: (str) -> None
        """
        Load and create the folder structure

        Args:
            project_root: Path of the project root
        """
        use_structure = "core/config/project_structures/joe_template.yml"
        project_structure = self.load_structure(use_structure)
        self.create_folder_structure(project_root, project_structure)
        self.project_root = project_root

    def create_folder_structure(self, project_root, structure):
        # type: (str, dict) -> None
        """
        Build the default folder structure

        Args:
            project_root: The project root folder
            structure: Folder structure to build
        """
        for p, v in self.iteritems_recursive(structure):
            sub_path = "/".join(list(p))
            folder_path = file_utils.join_file_names(project_root, sub_path)
            file_utils.create_directories(folder_path)

    def create_all_shot_folders(self):
        """
        Create the sequence folders
        """
        self.logger.info("Creating new sequence folders")
        for sequence_name, shots_list in self.create_dict.items():

            # create sequences
            sequence_dir = file_utils.join_file_names(self.project_root, "shots", sequence_name)
            file_utils.create_directory(sequence_dir)
            self.logger.info(f"Done creating sequence {sequence_name}")

            for shot_name in shots_list:
                shot_dir = file_utils.join_file_names(sequence_dir, shot_name)
                file_utils.create_directory(shot_dir)
                #self.logger.info(f"Done creating shot {shot_name}")

                # create tasks in the subfolders of a app
                # e.g. houdini/hip/modeling, houdini/hip/lighting
                #self.logger.info(core_constants.SHOT_STRUCTURE)
                shot_structure = self.load_structure(core_constants.SHOT_STRUCTURE)
                self.create_folder_structure(shot_dir, shot_structure)
                self.create_app_task_folders(shot_dir, "shot")

    def create_app_task_folders(self, root_folder, entity_type_name, use_task_list=None, app_list=None):
        # type: (str, str, Optional[list[str]], Optional[list[str]]) -> None
        """
        Create the task folders within a specific subfolder

        Args:
            root_folder: Main root folder of the asset or shot
            entity_type_name: Either s shot or build
            use_task_list: List of task names to create
            app_list: List of applications to create for
        """
        task_structure = self.load_structure(core_constants.TASK_STRUCTURE)
        #self.logger.info(f"Creating {entity_type_name} folders")
        for app, subfolders in task_structure.items():
            if app_list and app not in app_list:
                continue

            for subfolder, task_dict in subfolders.items():
                asset_subfolder_dir = file_utils.join_file_names(root_folder, app, subfolder)
                #self.logger.info(f"Creating {app} task folders under {root_folder}")

                task_list = use_task_list or task_dict[entity_type_name]
                #self.logger.info(f"Found tasks: {task_list}")

                for task_folder in task_list:
                    task_dir =  file_utils.join_file_names(asset_subfolder_dir, task_folder)
                    file_utils.create_directories(task_dir)

                    # if it is a source folder
                    user_dir = file_utils.join_file_names(task_dir, core_constants.USERNAME)
                    file_utils.create_directory(user_dir)

    def create_asset_folders(self):
        """
        Create the asset on disk and on ftrack
        """
        assets_dir = file_utils.join_file_names(self.project_root, "assets")
        file_utils.create_directory(assets_dir)

        for asset_build_type_name, asset_build_names in self.create_dict.items():
            # create the folder name of the asset
            asset_type_folder_dir = file_utils.join_file_names(assets_dir, asset_build_type_name)
            file_utils.create_directory(asset_type_folder_dir)

            for asset_build_name in asset_build_names:
                asset_build_name_dir = file_utils.join_file_names(asset_type_folder_dir, asset_build_name)
                file_utils.create_directory(asset_build_name_dir)

                # create asset app folder with default sub folders
                # e.g.houdini/hip, houdini/otls....
                asset_structure = self.load_structure(core_constants.ASSET_STRUCTURE)
                self.create_folder_structure(asset_build_name_dir, asset_structure)

                # create tasks in the subfolders of a app
                # e.g. houdini/hip/modeling, houdini/hip/lighting
                self.create_app_task_folders(asset_build_name_dir, "asset")

