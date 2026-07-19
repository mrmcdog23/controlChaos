""" Class to create folder structure on a project """
import os
from typing import Optional
import ccftrack.asset as asset
import ccftrack.shot as shot
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

        # initialise class variables
        self.project_name = project_name
        self.is_longform = self.ftshot.is_longform
        self.folder_structure = dict()
        self.create_dict = dict()
        self.root_dir = str()

    @property
    def project_root_dir(self):
        # type: () -> str
        """ The project root to create under """
        return self.root_dir or self.data.project_root

    def load_structure(self, structure):
        # type: (str) -> dict
        """
        Load the folder structure from the relevant yaml

        Args:
            structure: Path of the structure yaml file
        """
        folder_structure_path = self.data.get_relative_path(structure)
        return file_utils.read_yaml(folder_structure_path)

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
        if self.is_longform:
            use_structure = core_constants.LONGFORM_STRUCTURE
        else:
            use_structure = core_constants.COMMERICALS_STRUCTURE
        project_structure = self.load_structure(use_structure)
        self.create_folder_structure(project_root, project_structure)

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
            folder_path = os.path.join(project_root, sub_path)
            file_utils.create_directories(folder_path)

    def get_sequence_directory(self):
        # type: () -> str
        """
        Get the sequence directory based on
        whether its a commercial project or not

        Returns:
            sequence_dir: The sequence directory path
        """
        sequence_name = self.create_dict["sequence_name"]
        if self.is_longform:
            episode_name = self.create_dict["episode_name"]
            sequence_dir = file_utils.join_from_list(
                self.project_root_dir, "vfx", episode_name, sequence_name
            )
        else:
            sequence_dir = file_utils.join_from_list(
                self.project_root_dir, "vfx", sequence_name
            )
        return sequence_dir

    def create_all_shot_folders(self):
        """
        Create the shot directories under the sequences
        """
        self.create_episode_folders()
        self.create_sequence_folders()
        self.create_shot_folders()

    def create_episode_folders(self):
        """
        Create the sequence folders
        """
        if not self.is_longform:
            return

        self.logger.info("Creating new episode folders...")
        episode_name = self.create_dict.get("episode_name")
        if not episode_name:
            self.logger.warning("No episode names to create")
            return

        # create episode
        episode_dir = file_utils.join_from_list(
            self.project_root_dir, "vfx", episode_name
        )
        file_utils.create_directory(episode_dir)
        self.ftshot.create_episode(episode_name)
        self.logger.info(f"Done creating episode {episode_name} on ftrack")

    def create_sequence_folders(self):
        """
        Create the sequence folders
        """
        self.logger.info("Creating new sequence folders")
        episode_name = self.create_dict.get("episode_name")
        sequence_name = self.create_dict["sequence_name"]

        # create sequences
        sequence_dir = self.get_sequence_directory()
        file_utils.create_directory(sequence_dir)
        self.ftshot.create_sequence(sequence_name, episode_name=episode_name)
        self.logger.info(f"Done creating sequence {sequence_name} on ftrack")

    def create_shot_folders(self):
        """
        Create the shot folders from a list of shot dictionaries
        """
        episode_name = self.create_dict.get("episode_name")
        sequence_name = self.create_dict["sequence_name"]
        shot_dicts = self.create_dict["shot_dicts"]

        # get sequence root folder
        sequence_dir = self.get_sequence_directory()
        for shot_dict in shot_dicts:
            shot_name = shot_dict["name"]
            start = shot_dict.get("start")
            end = shot_dict.get("end")

            # create the shot root directory
            shot_root_dir = file_utils.join_from_list(sequence_dir, shot_name)
            file_utils.create_directory(shot_root_dir)

            # create tasks in the subfolders of a app
            # e.g. houdini/hip/modeling, houdini/hip/lighting
            self.logger.info(core_constants.SHOT_STRUCTURE)
            shot_structure = self.load_structure(core_constants.SHOT_STRUCTURE)
            self.create_folder_structure(shot_root_dir, shot_structure)
            self.create_app_task_folders(shot_root_dir, "shot")

            # create shot on ftrack
            self.ftshot.create_shot(
                shot_name,
                sequence_name,
                episode_name=episode_name,
                start=start,
                end=end,
            )

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
        self.logger.info(f"Creating {entity_type_name} folders")
        for app, subfolders in task_structure.items():
            if app_list and app not in app_list:
                continue

            for subfolder, task_dict in subfolders.items():
                asset_subfolder_dir = file_utils.join_from_list(root_folder, app, subfolder)
                self.logger.info(f"Creating {app} task folders under {root_folder}")
                task_list = use_task_list or task_dict[entity_type_name]
                self.logger.info(f"Found tasks: {task_list}")

                for task_folder in task_list:
                    task_dir = os.path.join(asset_subfolder_dir, task_folder)
                    file_utils.create_directories(task_dir)
                    # if it is a source folder
                    if subfolder not in core_constants.SOURCE_FOLDER:
                        continue
                    for wip_or_pub in ["wip", "pub"]:
                        wip_or_pub_dir = file_utils.join_from_list(task_dir, wip_or_pub)
                        file_utils.create_directory(wip_or_pub_dir)

    def create_asset_folders(self, add_to_ftrack=True):
        """
        Create the asset on disk and on ftrack
        """
        root_dir = file_utils.join_from_list(self.project_root_dir, "vfx", "build")
        file_utils.create_directory(root_dir)

        # create the folder name of the asset
        asset_build_type_name = self.create_dict["asset_build_type_name"]
        asset_build_name = self.create_dict["asset_build_name"]

        # create the folder directory
        suffix = core_constants.BUILD_MAPPINGS[asset_build_type_name]
        build_name = f"{suffix}{asset_build_name}"
        asset_folder_dir = file_utils.join_from_list(root_dir, build_name)
        file_utils.create_directory(asset_folder_dir)

        # create asset app folder with default sub folders
        # e.g.houdini/hip, houdini/otls....
        asset_structure = self.load_structure(core_constants.ASSET_STRUCTURE)
        self.create_folder_structure(asset_folder_dir, asset_structure)

        # create tasks in the subfolders of a app
        # e.g. houdini/hip/modeling, houdini/hip/lighting
        self.create_app_task_folders(asset_folder_dir, "asset")

        # create the asset on ftrack
        if not add_to_ftrack:
            return
        self.ftasset.create_ftrack_asset(asset_build_type_name,
                                         build_name,
                                         )

