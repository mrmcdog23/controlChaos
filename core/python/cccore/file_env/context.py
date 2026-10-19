""" File to set and get file paths and values """
import os
import glob
from typing import Optional
import cccore.data.server_data as server_data
import cccore.utils.file_utils as file_utils
import cccore.utils.cc_logging as cc_logging
from cccore.file_env import ctx_constants
import cccore.core_constants as core_constants


class Context(object):
    """
    Get the current context from the environment variable
    """
    def __init__(self, overrides=None):
        # type: (Optional[dict]) -> None
        """
        Args:
            overrides: Dictionary of information to override
                       the ones found in the environment
        """
        self.overrides = overrides or dict()
        self.use_aov = self.overrides.get("aov")
        self.use_ext = self.overrides.get("ext")
        self.use_app = self.overrides.get("app_name")
        self.use_suffix = self.overrides.get("suffix")
        self.use_subfolder = self.overrides.get("subfolder")
        self.use_frame_num = self.overrides.get("frame_num", "####")
        self.use_jobs_dir = self.overrides.get("jobs_dir")

        self.use_is_single_frame_sequence = None
        self.use_version = None
        self.use_task = None
        self.use_username = None
        self.use_ingest_subfolder = None
        self.project_data = server_data.ProjectData()
        self.logger = cc_logging.cc_logger()

    @property
    def is_asset(self):
        # type: () -> bool
        """ Is it an asset build """
        return bool(self.entity == ctx_constants.ASSET)

    def get_value(self, key_name):
        # type: (str) -> str
        """
        Get a key value from the various forms in order
        """
        return self.overrides.get(key_name) or os.environ.get(key_name.upper()) or os.environ.get(key_name)

    @property
    def jobs_dir(self):
        # type: () -> str
        """ Use the job root directory """
        return os.path.dirname(self.project_root)

    @property
    def project_name(self):
        # type: () -> str
        """ Name of the project """
        return self.get_value("project_name")

    @property
    def project_code(self):
        # type: () -> str
        """ Code of the project """
        return self.get_value("project_code")
    @property
    def project_root(self):
        # type: () -> str
        """ Path of the root folder """
        return self.get_value("project_root")

    @property
    def episode(self):
        return None

    @property
    def sequence(self):
        # type: () -> str
        """ Name of the sequence """
        return self.get_value("sequence_name")

    @property
    def shot(self):
        # type: () -> str
        """ Name of the shot """
        return self.get_value("shot_name")

    @property
    def asset_type(self):
        # type: () -> str
        """ Name of the asset type """
        return self.get_value("asset_type")

    @property
    def asset_name(self):
        # type: () -> str
        """ Get the current asset name """
        return self.get_value("asset_name")

    @property
    def app_name(self):
        # type: () -> str
        """ Get the current application name """
        return self.get_value("app_name")

    @property
    def username(self):
        # type: () -> str
        """ Get the current application name """
        return self.use_username if self.use_username else self.get_value("username")

    @property
    def project_shots_dir(self):
        # type: () -> str
        """ The project shots directory """
        return file_utils.join_file_names(self.project_root, ctx_constants.SEQUENCE)

    @property
    def project_assets_dir(self):
        # type: () -> str
        """ The project assets directory """
        return file_utils.join_file_names(self.project_root, ctx_constants.ASSET)

    @property
    def task(self):
        # type: () -> str
        """ Name of the task """
        return self.use_task if self.use_task else self.get_value("task_name")

    @property
    def suffix(self):
        # type: () -> str
        """ Name of the suffix """
        return self.use_suffix or self.get_value("suffix") or str()

    @property
    def suffix_str(self):
        # type: () -> str
        """ Name of the file suffix """
        return f"_{self.suffix}" if self.suffix else str()

    @property
    def sequence_dir(self):
        # type: () -> str
        """ The project shots directory """
        return file_utils.join_file_names(self.project_shots_dir, self.sequence)

    @property
    def shot_dir(self):
        # type: () -> str
        """ The project shots directory """
        return file_utils.join_file_names(self.sequence_dir, self.shot)

    @property
    def app_dir(self):
        # type: () -> str
        """ The project shots directory """
        if self.is_asset:
            return file_utils.join_file_names(self.asset_name_dir, self.app_name)
        else:
            return file_utils.join_file_names(self.shot_dir, self.app_name)

    @property
    def subfolder_dir(self):
        # type: () -> str
        """ The project shots directory """
        return file_utils.join_file_names(self.app_dir, self.file_subfolder)

    @property
    def abc_dir(self):
        # type: () -> str
        """ The project abc directory """
        return file_utils.join_file_names(self.app_dir, "abc", self.task)

    @property
    def cache_dir(self):
        # type: () -> str
        """ The project cache directory """
        return file_utils.join_file_names(self.app_dir, "cache", self.task)

    @property
    def usd_dir(self):
        # type: () -> str
        """ The project usd directory """
        return file_utils.join_file_names(self.app_dir, "usd", self.task)

    @property
    def data_dir(self):
        # type: () -> str
        """ The project data directory """
        return file_utils.join_file_names(self.app_dir, "data", self.task)

    @property
    def movie_dir(self):
        # type: () -> str
        """ The project shots directory """
        return file_utils.join_file_names(self.app_dir, "movie", self.task)

    @property
    def render_dir(self):
        # type: () -> str
        """ The project render directory """
        return file_utils.join_file_names(self.app_dir, "render", self.task)

    @property
    def task_dir(self):
        # type: () -> str
        """ The project shots directory """
        return file_utils.join_file_names(self.subfolder_dir, self.task)

    @property
    def user_dir(self):
        # type: () -> str
        """ The project shots directory """
        return file_utils.join_file_names(self.task_dir, self.username)

    @property
    def asset_type_dir(self):
        # type: () -> str
        """ The project asset type directory """
        return file_utils.join_file_names(self.project_assets_dir, self.asset_type)

    @property
    def asset_name_dir(self):
        # type: () -> str
        """ The project asset name directory """
        return file_utils.join_file_names(self.asset_type_dir, self.asset_name)

    @property
    def file_subfolder(self):
        # type: () -> str
        """ The application subfolder """
        return ctx_constants.APP_FILE_SUBFOLDER[self.app_name]

    @property
    def file_name(self):
        # type: () -> str
        """ Build the file name without the extension """
        if self.is_asset:
            return f"{self.project_code}_{self.asset_type}_{self.asset_name}_{self.task}{self.suffix_str}"
        else:
            return f"{self.project_code}_{self.sequence}_{self.shot}_{self.task}{self.suffix_str}"

    @property
    def is_image(self):
        # type: () -> bool
        """ It is an image sequence in the current extension """
        return self.ext in core_constants.IMAGE_TYPES

    @property
    def is_sequence(self):
        # type: () -> bool
        """
        It is an image sequence in the current extension
        """
        return self.ext in core_constants.SEQUENCE_TYPES

    @property
    def is_single_frame_sequence(self):
        # type: () -> bool
        """
        Is the sequence a single frame
        """
        if self.use_is_single_frame_sequence is not None:
            return self.use_is_single_frame_sequence
        return self.ext in core_constants.SINGLE_FRAME_SEQUENCE

    @property
    def next_save_path(self):
        # type: () -> str
        """ Work out what the next wip file path will be """
        file_path, _ = self.get_next_save_path(self.user_dir)
        return file_path

    @property
    def next_save_version(self):
        # type: () -> int
        """ Get the next save version on disk """
        _, version_num = self.get_next_save_path(self.user_dir)
        return version_num

    def set_next_save_version(self):
        self.use_version = self.next_save_version

    def get_next_save_path(self, save_dir):
        # type: (str) -> Optional[str]
        """
        Get the next file path of the wip file

        Args:
            save_dir: Directory to save file to.

        Returns:
            file_path: The next path to save
        """
        file_path = None
        file_exists = True
        current_file_list = glob.glob(f"{save_dir}/*{self.ext}")
        version_num = len(current_file_list) + 1

        while file_exists:
            self.use_version = version_num
            file_path = file_utils.join_file_names(save_dir, self.new_filename)
            file_exists = os.path.exists(file_path)
            version_num += 1
            if version_num == 200:
                return None, None
        return file_path, version_num

    @property
    def save_file_path(self):
        # type: () -> str
        """ Get the save file path from data given"""
        return file_utils.join_file_names(self.user_dir, self.new_filename)

    @property
    def ext(self):
        # type: () -> str
        """ Get the file extension. Can be overridden with use_ext """
        return self.use_ext

    @property
    def is_sequence(self):
        # type: () -> bool
        """ It is an image sequence in the current extension """
        return self.ext in core_constants.SEQUENCE_TYPES

    @property
    def new_filename(self):
        # type: () -> str
        """ Get the new file name including the extension """
        if self.version_padded:
            version_padded = self.version_padded
        else:
            version_padded = str(self.use_version).zfill(3)
        if self.is_sequence and not self.is_single_frame_sequence:
            sequence_file_name = f"{self.file_name}_v{version_padded}.####.{self.ext}"
        else:
            sequence_file_name = f"{self.file_name}_v{version_padded}.{self.ext}"
        return sequence_file_name

    @property
    def entity(self):
        # type: () -> Optional[str]
        """ The entity type e.g. build or shot """
        return self.get_value("entity")

    @property
    def version_padded(self):
        # type: () -> str
        """ Version number as a padded string """
        if self.use_version:
            return str(self.use_version).zfill(3)
        version_padded = self.get_value("version_padded")
        if version_padded:
            return version_padded

    @property
    def version_int(self):
        # type: () -> int
        """ Version number as a n integer """
        if self.use_version:
            return self.use_version
        if self.version_padded:
            return int(self.version_padded)

    @property
    def alembic_file_path(self):
        # type: () -> str
        """ Work out the next abc save path """
        self.use_ext = "abc"
        alembic_path = file_utils.join_file_names(
            self.abc_dir, f"v{self.version_padded}", self.new_filename)
        return alembic_path

    @property
    def fbx_file_path(self):
        # type: () -> str
        """ Work out the next fbx save path """
        self.use_ext = "fbx"
        fbx_path = file_utils.join_file_names(
            self.cache_dir, f"v{self.version_padded}", self.new_filename)
        return fbx_path

    @property
    def usd_file_path(self):
        # type: () -> str
        """ Work out the next fbx save path """
        self.use_ext = "usd"
        usd_path = file_utils.join_file_names(
            self.usd_dir, f"v{self.version_padded}", self.new_filename)
        return usd_path
    
    @property
    def data_file_path(self):
        # type: () -> str
        """ Work out the next fbx save path """
        self.use_ext = "json"
        fbx_path = file_utils.join_file_names(
            self.data_dir, f"v{self.version_padded}", self.new_filename)
        return fbx_path

    @property
    def playblast_movie_path(self):
        # type: () -> str
        """ Path of the sequence cache file """
        self.use_ext = "mov"
        if os.path.exists(self.movie_dir):
            self.use_version = len(os.listdir(self.movie_dir)) + 1
        else:
            self.use_version = 1
        return file_utils.join_file_names(self.data_dir, self.new_filename)

    @property
    def render_sequence_path(self):
        # type: () -> str
        """ Path of the render sequence file """
        return file_utils.join_file_names(self.render_dir, self.new_filename)

    @property
    def as_dict(self):
        # type: () -> dict
        """
        Get a dictionary of the values

        Returns:
            context_dict: The information of the values
        """
        context_dict = {
            "project_root": self.project_root,
            "entity": self.entity,
            "task_name": self.task,
            "app_name": self.app_name,
            "subfolder": self.file_subfolder,
            "ext": self.ext,
            "project_name": self.project_name,
            "version_padded": self.version_padded,
            "version_num": self.version_int,
            "suffix": self.suffix
        }
        if self.entity == ctx_constants.ASSET:
            context_dict["asset_type"] = self.asset_type
            context_dict["asset_name"] = self.asset_name
        else:
            context_dict["sequence_name"] = self.sequence
            context_dict["shot_name"] = self.shot
        return context_dict
