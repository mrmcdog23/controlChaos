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
        self.use_ingest_subfolder = None
        self.project_data = server_data.ProjectData()
        self.logger = cc_logging.cc_logger()

    @property
    def is_build(self):
        # type: () -> bool
        """ Is it an asset build """
        return bool(self.entity == "asset")

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
    def app_name(self):
        # type: () -> str
        """ Get the current application name """
        return self.get_value("app_name")

    @property
    def username(self):
        # type: () -> str
        """ Get the current application name """
        return self.get_value("username")

    @property
    def project_shots_dir(self):
        # type: () -> str
        """ The project shots directory """
        return file_utils.join_file_names(self.project_root, "shots")

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
        return file_utils.join_file_names(self.shot_dir, self.app_name)

    @property
    def subfolder_dir(self):
        # type: () -> str
        """ The project shots directory """
        return file_utils.join_file_names(self.app_dir, self.file_subfolder)

    @property
    def abc_dir(self):
        # type: () -> str
        """ The project shots directory """
        return file_utils.join_file_names(self.app_dir, "abc", self.task)

    @property
    def cache_dir(self):
        # type: () -> str
        """ The project shots directory """
        return file_utils.join_file_names(self.app_dir, "cache", self.task)

    @property
    def data_dir(self):
        # type: () -> str
        """ The project shots directory """
        return file_utils.join_file_names(self.app_dir, "data", self.task)

    @property
    def movie_dir(self):
        # type: () -> str
        """ The project shots directory """
        return file_utils.join_file_names(self.app_dir, "movie", self.task)

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

    #C:/Users/joele/Documents/PAU/shots/seq010/shot010/maya/scenes/layout/jleveson/PAU_seq010_shot0100_layout_v001.ma

    @property
    def file_subfolder(self):
        # type: () -> str
        """ The application subfolder """
        return ctx_constants.APP_FILE_SUBFOLDER[self.app_name]

    @property
    def file_name(self):
        # type: () -> str
        """ Build the file name without the extension"""
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
        return self.get_next_save_path(self.user_dir)

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
            file_path = os.path.join(save_dir, self.new_filename)
            file_exists = os.path.exists(file_path)
            version_num += 1
            if version_num == 200:
                return None
        return file_path

    @property
    def ext(self):
        # type: () -> str
        """ Get the file extension. Can be overridden with use_ext """
        return self.use_ext

    @property
    def new_filename(self):
        version_padded = str(self.use_version).zfill(3)
        return f"{self.file_name}_v{version_padded}.{self.ext}"

    @property
    def entity(self):
        # type: () -> Optional[str]
        """ The entity type e.g. build or shot """
        return self.get_value("entity")

    @property
    def version_padded(self):
        # type: () -> str
        """ Version number as a padded string """
        version_padded = self.get_value("version_padded")
        if version_padded:
            return version_padded
        if self.use_version:
            return str(self.use_version).zfill(3)

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
        """
        Path of the sequence cache file
        """
        self.use_ext = "mov"
        if os.path.exists(self.movie_dir):
            self.use_version = len(os.listdir(self.movie_dir)) + 1
        else:
            self.use_version = 1
        return file_utils.join_file_names(self.data_dir, self.new_filename)

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
        return context_dict

    '''
    @property
    def vfx_dir(self):
        # type: () -> str
        """ vfx directory folder """
        return file_utils.join_from_list(self.project_root, core_constants.VFX)

    @property
    def appdata_dir(self):
        # type: () -> str
        """ The project appdata directory """
        return file_utils.join_from_list(self.vfx_dir, "appdata")

    @property
    def flipbook_dir(self):
        # type: () -> str
        """ The project flipbook directory """
        return file_utils.join_from_list(self.appdata_dir, "flipbook")

    @property
    def build_type(self):
        # type: () -> Optional[str]
        """
        Build type such as Prop or Character. Found by
        the prefix and checking the mappings.
        """
        if not self.asset_build:
            return str()
        prefix = self.asset_build[:2]
        inv_map = {v: k for k, v in core_constants.BUILD_MAPPINGS.items()}
        return inv_map[prefix]

    def get_value(self, key_name):
        # type: (str) -> str
        """
        Get a key value from the various forms in order
        """
        return self.overrides.get(key_name) or os.environ.get(key_name.upper()) or os.environ.get(key_name)

    @property
    def asset_build(self):
        # type: () -> str
        """ The asset build name """
        return self.get_value("asset_build_name")

    @property
    def episode(self):
        # type: () -> str
        """ Name of the sequence """
        return self.get_value("episode_name")

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
    def full_sequence_name(self):
        # type: () -> str
        """ Get the full sequence name """
        if self.episode:
            return f"{self.episode}_{self.sequence}"
        return self.sequence

    @property
    def full_shot_name(self):
        # type: () -> str
        """ Get the full shot name """
        return f"{self.full_sequence_name}_{self.shot}"

    @property
    def task(self):
        # type: () -> str
        """ Name of the task """
        return self.use_task if self.use_task else self.get_value("task_name")

    @property
    def app(self):
        # type: () -> str
        """
        Name of the app e.g. maya, houdini, nuke
        """
        if self.ext == "nk":
            self.use_app = "nuke"
        elif self.ext == "ma":
            self.use_app = "maya"
        return self.use_app or self.get_value("app_name")

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
    def sequence_base_name(self):
        # type: () -> str
        """ Get the sequence base name """
        return self.overrides.get("sequence_base_name")

    def get_app_subfolder(self):
        # type: () -> str
        """
        Get the relevant subfolder from the current
        app by using the task structure and finding
        it in the dictionary
        """
        task_structure_path = self.project_data.get_relative_path(core_constants.TASK_STRUCTURE)
        task_structure = file_utils.read_yaml(task_structure_path)

        # always use the first one in the subfolder list
        subfolder_dict = task_structure.get(self.app)
        if not subfolder_dict:
            return str()

        subfolder_keys = subfolder_dict.keys()
        subfolder = list(subfolder_keys)[0]
        return subfolder

    @property
    def subfolder(self):
        # type: () -> str
        """
        The application subfolder
        """
        if self.use_subfolder:
            return self.use_subfolder

        subfolder = self.get_value("subfolder")
        if not subfolder:
            subfolder = self.get_app_subfolder()

        # if it's an alembic file then export to abc directory
        if self.is_image:
            subfolder = "render"
        if self.ext == "nk":
            subfolder = "scripts"
        if self.ext == "abc":
            subfolder = "abc"
        if self.ext == "3de":
            subfolder = "3de"
        if self.ext in ["fbx", "obj"]:
            subfolder = "cache"
        return subfolder

    @property
    def version(self):
        # type: () -> Optional[str]
        """
        Version number as an unpadded string
        """
        version_params = [self.use_version,
                          self.overrides.get('version_num'),
                          os.environ.get("version_num"),
                          self.overrides.get('version')
                          ]
        for value in version_params:
            if value is not None:
                return str(value)

    @property
    def version_int(self):
        # type: () -> Optional[int]
        """ The version number as integer """
        for version_variable in [self.version, self.version_padded]:
            try:
                return int(version_variable)
            except (ValueError, TypeError):
                pass

    @property
    def version_padded(self):
        # type: () -> str
        """ Version number as a padded string """
        return str(self.version).zfill(3)

    @property
    def is_build(self):
        # type: () -> bool
        """ Is it an asset build """
        return bool(self.entity == "build")

    @property
    def is_shot(self):
        # type: () -> bool
        """ Is it a shot """
        return bool(self.entity == "shot")

    @property
    def wip_or_pub(self):
        # type: () -> str
        """
        Is the folder wip or pub
        """
        return self.overrides.get('wip_or_pub', 'pub')

    @property
    def is_pub(self):
        # type: () -> bool
        """ Is the context published """
        return self.wip_or_pub == "pub"

    @property
    def ext(self):
        # type: () -> str
        """ Get the file extension. Can be overridden with use_ext """
        return self.use_ext

    @property
    def aov(self):
        # type: () -> str
        """ The current aov name """
        return self.use_aov

    @property
    def aov_str(self):
        # type: () -> str
        """
        The aov as a string format. Add an underscore
        for the aov name if there is one
        """
        return "_{}".format(self.aov) if self.aov else ""

    @property
    def frame_num(self):
        # type: () -> str
        """ Frame number to use in text """
        return str(self.use_frame_num)

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
    def entity_root_dir(self):
        # type: () -> Optional[str]
        """
        Find the current asset build root

        Returns:
            root_dir: Path of the entity root
        """
        if self.wip_dir and self.app:
            return self.wip_dir.split("/" + self.app)[0]

    @property
    def shot_dir(self):
        # type: () -> str
        """ The shot directory """
        folder_list = [
                self.project_root,
                core_constants.VFX,
                self.sequence,
                self.shot
            ]
        if self.episode:
            folder_list.insert(2, self.episode)
        return file_utils.join_from_list(folder_list)

    @property
    def asset_build_dir(self):
        # type: () -> str
        """ The asset name directory """
        folder_list = [self.project_root,
                       core_constants.VFX,
                       core_constants.BUILD,
                       self.asset_build
                       ]
        return file_utils.join_from_list(folder_list)

    @property
    def subfolder_dir(self):
        # type: () -> str
        """ Get the directory above the task folder """
        return os.path.dirname(self.task_dir)

    @property
    def app_dir(self):
        # type: () -> str
        """ Get the directory above the subdirectory folder """
        return os.path.dirname(self.subfolder_dir)

    @property
    def source_dir(self):
        # type: () -> str
        """ The source directory of a shot """
        return file_utils.join_from_list(self.shot_dir, "source")

    @property
    def flame_exr_dir(self):
        # type: () -> str
        """ The flame exr export directory of a shot """
        return file_utils.join_from_list(self.shot_dir, "flame", "exr")

    @property
    def task_dir(self):
        # type: () -> Optional[str]
        """
        From the context workout the current workspace directory

        Returns:
            context_dir: The current directory of the context
        """
        # get the template format
        if self.is_build:
            path_format = BUILD_TASK_DIR_FMT
        else:
            path_format = SHOT_TASK_DIR_FMT

        task_dir = self.format_name_from_dict(path_format)
        if not task_dir:
            return None
        task_dir_clean = task_dir.replace("\\", "/")
        return task_dir_clean

    @property
    def metadata_dir(self):
        # type: () -> str
        """
        Get the current metadata directory

        Returns:
            metadata_dir: Path of the metadata directory
        """
        metadata_dir = os.path.join(self.wip_dir, ".metadata")
        metadata_dir = metadata_dir.replace("\\", "/")
        return metadata_dir

    @property
    def metadata_path(self):
        # type: () -> str
        """
        Path of the file metadata
        """
        self.use_ext = "metadata"
        self.overrides["wip_or_pub"] = "wip"
        self.overrides["subfolder"] = self.get_app_subfolder()
        metadata_path = file_utils.join_from_list(self.metadata_dir, self.new_filename)
        return metadata_path

    @property
    def wip_dir(self):
        # type: () -> str
        """ The current context wip directory """
        wip_dir = "{task_dir}/wip".format(task_dir=self.task_dir)
        return wip_dir

    @property
    def pub_dir(self):
        # type: () -> str
        """ The current context publish directory """
        pub_dir = "{wip_dir}/pub".format(wip_dir=self.task_dir)
        return pub_dir

    @property
    def is_valid(self):
        # type: () -> bool
        """ Is the context set and valid """
        if self.task_dir is None:
            return False
        return True

    @property
    def latest_wip_path(self):
        # type: () -> Optional[str]
        """ Work out what the next wip file path will be """
        self.overrides["wip_or_pub"] = "wip"
        wip_file_paths = glob.glob(f"{self.wip_dir}/*{self.use_ext}")
        if not wip_file_paths:
            return str()
        wip_file_paths.sort()
        return wip_file_paths[-1]

    @property
    def next_wip_save_path(self):
        # type: () -> str
        """ Work out what the next wip file path will be """
        self.overrides["wip_or_pub"] = "wip"
        return self.next_no8_save_path(self.wip_dir)

    def next_pub_save_path(self):
        # type: () -> str
        """
        Work out what the next pub file path will be

        Returns:
            Next pub file path to save
        """
        self.overrides["wip_or_pub"] = "pub"
        file_path = file_utils.join_from_list(self.pub_dir, self.new_filename)
        return file_path.replace("\\", "/")

    @property
    def new_filename(self):
        # type: () -> str
        """ Get the file name from the context and information """
        filename_format = BUILD_FILE_NAME_FMT if self.is_build else SHOT_FILE_NAME_FMT
        filename = self.format_name_from_dict(filename_format)
        if self.is_sequence and not self.is_single_frame_sequence:
            name = file_utils.get_file_name(filename)
            filename = "{name}.####.{ext}".format(name=name,
                                                  ext=self.ext
                                                  )

        return filename

    def next_no8_save_path(self, save_dir):
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
            file_path = os.path.join(save_dir, self.new_filename)
            file_exists = os.path.exists(file_path)
            version_num += 1
            if version_num == 200:
                return None
        return file_path

    @property
    def wip_file_path(self):
        # type: () -> str
        """ The wip file path """
        self.overrides['wip_or_pub'] = 'wip'
        file_path = file_utils.join_from_list(self.wip_dir, self.new_filename)
        return file_path

    @property
    def pub_file_path(self):
        # type: () -> str
        """ The published file path """
        self.overrides['wip_or_pub'] = 'pub'
        file_path = file_utils.join_from_list(self.pub_dir, self.new_filename)
        return file_path

    @property
    def ingest_sub_folder(self):
        # type: () -> str
        """ Get the ingester subfolder path """
        subfolder = f"{self.full_shot_name}_{self.use_task}_{self.version_padded}"
        ingest_in_list = [self.shot_dir, self.use_task, "in", subfolder, self.use_ingest_subfolder]
        return file_utils.join_from_list(ingest_in_list)

    @property
    def ingest_file_path(self):
        # type: () -> str
        """ Get the ingester file path """
        if self.is_sequence:
            ingest_folder_list = [self.ingest_sub_folder, self.sequence_file_name]
        else:
            ingest_folder_list = [self.ingest_sub_folder, self.new_filename]
        return file_utils.join_from_list(ingest_folder_list)

    @property
    def maya_cache_dir(self):
        # type: () -> str
        """ The maya cache directory path """
        cache_in_list = [self.shot_dir, "maya", "cache"]
        return file_utils.join_from_list(cache_in_list)

    @property
    def sequence_path(self):
        # type: () -> str
        """
        Get the image sequence path for a frame path

        Returns:
            sequence_path: Path of the sequence: /job/render.####.png
        """
        self.overrides['wip_or_pub'] = 'pub'
        folder_list = [self.task_dir, self.version_padded, self.sequence_file_name]
        sequence_path = file_utils.join_from_list(folder_list)
        return sequence_path

    @property
    def win_sequence_path(self):
        # type: () -> str
        """ The sequences in windows format """
        sequence_path = self.sequence_path
        win_sequence_path = sequence_path.replace("/mnt", "//192.168.1.10/storage")
        return win_sequence_path

    @property
    def hou_sequence_path(self):
        # type: () -> str
        """
        The next possible hou sequence path
        """
        return self.sequence_path.replace(".####.", ".$F4.")

    @property
    def otls_sequence_path(self):
        # type: () -> str
        """
        The alembic sequence path
        """
        self.use_subfolder = "otls"
        self.use_ext = "cpio"
        return self.sequence_path

    @property
    def abc_sequence_path(self):
        # type: () -> str
        """
        The alembic sequence path
        """
        self.use_subfolder = "abc"
        self.use_ext = "abc"
        return self.sequence_path

    @property
    def usd_path(self):
        # type: () -> str
        """ The usd asset path """
        self.use_subfolder = "usd"
        self.use_ext = "usd"
        return self.sequence_path

    @property
    def fbx_sequence_path(self):
        # type: () -> str
        """
        The fbx sequence path
        """
        self.use_subfolder = "cache"
        self.use_ext = "fbx"
        return self.sequence_path

    @property
    def cache_sequence_path(self):
        # type: () -> str
        """
        Path of the sequence cache file
        """
        self.overrides["subfolder"] = "cache"
        return self.sequence_path

    @property
    def playblast_movie_path(self):
        # type: () -> str
        """
        Path of the sequence cache file
        """
        self.overrides["subfolder"] = "movies"
        self.use_ext = "mov"
        self.use_aov = "pb"
        if os.path.exists(self.subfolder_dir):
            self.use_version = len(os.listdir(self.subfolder_dir)) + 1
        else:
            self.use_version = 1
        folder_list = [self.subfolder_dir, self.sequence_file_name]
        playblast_path = file_utils.join_from_list(folder_list)
        return playblast_path

    def format_name_from_dict(self, text_format):
        # type: (str) -> Optional[str]
        """
        From a format use the class values to make the string

        Args:
            text_format: Text format

        Returns:
            filename: Name of the file created
        """
        context_as_dict = self.as_dict()

        # from the format extract the keys to set
        pattern = r'(?<=\{).+?(?=\})'
        keys_to_find = re.findall(pattern, text_format)

        # check the context dictionary all values
        # are set and add a raise if not. If good
        # add to the dictionary to apply
        values_to_set = dict()
        for key in keys_to_find:
            value = context_as_dict.get(key)
            if value is None or value == "None":
                self.logger.critical(f"Not all values are valid: {key}")
                return None
            values_to_set[key] = value

        # apply the values to the text format
        filename = text_format.format(**values_to_set)
        return filename

    @property
    def sequence_file_name(self):
        # type: () -> str
        """
        Get the file name from the context and information

        Returns:
            sequence_file_name: File name constructed
        """
        if self.is_build:
            filename_format = BUILD_SEQ_NAME_FMT
        else:
            filename_format = SHOT_SEQ_NAME_FMT
        filename = self.format_name_from_dict(filename_format)

        if self.is_single_frame_sequence:
            sequence_file_name = f"{filename}.{self.ext}"
        else:
            sequence_file_name = f"{filename}.####.{self.ext}"
        return sequence_file_name

    @property
    def next_sequence_version(self):
        # type: () -> int
        """
        Get the next version sequence number
        """
        if not self.task:
            raise TypeError("Task is not set")
        if not self.aov:
            raise TypeError("Aov is not set")

        aov_dir = self.task_dir
        if not os.path.exists(aov_dir):
            return 1

        versions = os.listdir(aov_dir)
        version_nums = [ver for ver in versions if ver.isdigit()]
        if not version_nums:
            return 1
        version_nums.sort()
        return int(version_nums[-1]) + 1

    def use_next_sequence_version(self):
        """
        If use next sequence version set it as the use version
        """
        self.use_version = self.next_sequence_version

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
                        "app_name": self.app,
                        "subfolder": self.subfolder,
                        "ext": self.ext,
                        "project_name": self.project_name,
                        "version_padded": self.version_padded,
                        "version_num": self.version_int
                        }
        if self.is_build:
            context_dict["asset_build_type_name"] = self.build_type
            context_dict["asset_build_name"] = self.asset_build
        else:
            context_dict["episode_name"] = self.episode
            context_dict["sequence_name"] = self.sequence
            context_dict["shot_name"] = self.shot

        # set the mount root
        context_dict["jobs_dir"] = self.jobs_dir
        context_dict["aov"] = self.aov
        context_dict["suffix"] = self.suffix
        context_dict["suffix_str"] = self.suffix_str
        context_dict["aov_str"] = self.aov_str
        context_dict["version"] = self.version
        context_dict["version_padded"] = self.version_padded
        context_dict["version_num"] = self.version_int
        context_dict["wip_or_pub"] = self.wip_or_pub
        context_dict["vfx"] = core_constants.VFX
        context_dict["build"] = core_constants.BUILD

        return context_dict
        '''
