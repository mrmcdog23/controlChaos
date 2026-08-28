""" Ftrack asset version class for component management """
import os
import shutil
import collections
import ftrack_api
from typing import Optional
from ccftrack.base import FtBase
import cccore.core_constants as core_constants
import cccore.file_env.context_utils as context_utils
import cccore.utils.file_utils as file_utils


SCENE_ASSETS = "scene_assets"


class FtAssetVersion(FtBase):
    """
    Wrapper for querying and retrieving ftrack
    asset version and its components data
    """
    def __init__(self, input_project=None, session=None, log=True):
        # type: (Optional[str], Optional[ftrack_api.Session], Optional[bool]) -> None
        """
        Args:
            input_project: Name of the project to set to
            session: Ftrack session connection
            log: Whether to run the logger
        """
        self._component = None
        self._asset_version = None
        self._asset_version_id = None
        super(FtAssetVersion, self).__init__(input_project=input_project,
                                             session=session,
                                             log=log
                                             )

    def get_asset_version_from_id(self, id_):
        # type: (str) -> ftrack_api.entity.asset_version
        """
        From an id get the asset version

        Args:
            id_: The ftrack id to get the asset version with

        Returns:
            asset_version: The found asset version
        """
        asset_version = self.session.get('AssetVersion', id_)
        return asset_version

    @property
    def asset_version_id(self):
        # type: () -> str
        """ The current ftrack asset version id """
        return self._asset_version_id

    @property
    def wip_file_path(self):
        # type: () -> str
        """ Get the wip file path if it exists """
        return self.asset_version["custom_attributes"]["wip_file_path"]

    @asset_version_id.setter
    def asset_version_id(self, asset_version_id):
        # type: (str) -> None
        """
        Setter of the ftrack id. Needs to valid the asset version exists

        Args:
            asset_version_id: Version id to set it to
        """
        asset_version = self.get_asset_version_from_id(asset_version_id)
        if not asset_version:
            self.logger.error(f"Asset version not found with id: {asset_version_id}")
            return
        self._asset_version_id = asset_version_id
        self.logger.info(f"Asset version found with id: {asset_version_id}")
        self.asset_version = asset_version

    @property
    def asset_version(self):
        # type: () -> ftrack_api.entity.assetversion
        """
        Current set assets version
        """
        return self._asset_version

    @asset_version.setter
    def asset_version(self, asset_version):
        # type: (ftrack_api.entity.asset_version) -> None
        """
        Set the asset version
        """
        self._asset_version = asset_version

    def get_asset_version_url(self, asset_version):
        # type: (ftrack_api.entity.asset_version) -> str
        """
        From a ftrack asset version get the url for it

        Args:
            asset_version: The given ftrack asset version

        Returns:
            url_template: The ftrack url of the asset version
        """
        version_data = {'server_url': self.server_data.ftrack_url,
                        'version_id': asset_version['id'],
                        'project_id': asset_version['link'][0]['id']
                        }

        url_template = (
            '{server_url}#slideEntityId={version_id}'
            '&slideEntityType=assetversion'
            '&view=tasks'
            '&itemId=projects'
            '&entityId={project_id}'
            '&entityType=show'
        ).format(**version_data)
        return url_template

    @property
    def asset_version_url(self):
        # type: () -> str
        """
        The current asset ftrack url
        """
        return self.get_asset_version_url(self.asset_version)

    @property
    def html_link_format(self):
        # type: () -> str
        """
        The html link to the asset in green colour format
        """
        html_format = '<a href="{url}" style="color: #00bf60">{version_id} </a>'
        url_text = html_format.format(
            url=self.asset_version_url, version_id=self.asset_version_id)
        return url_text

    @property
    def metadata_path(self):
        # type: () -> str
        """
        Path of the scene data component
        """
        return self.get_component_path("Metadata")

    @property
    def metadata(self):
        # type: () -> dict
        """
        Get the scene metadata as a dictionary
        """
        if not self.metadata_path:
            return dict()
        return file_utils.read_json(self.metadata_component_path)

    @property
    def av_metadata(self):
        # type: () -> dict
        """ asset version metadata dictionary in readable format """
        metadata_dict = dict()
        for key, value in self.asset_version["metadata"].items():
            metadata_dict[key] = value
        return metadata_dict

    @property
    def scene_assets(self):
        # type: () -> dict
        """ Get the scene asset dictionary """
        return self.metadata.get(SCENE_ASSETS, dict())

    @property
    def locators(self):
        # type: () -> list[str]
        """ Get the locators dictionary """
        return self.metadata.get(core_constants.LOCATOR_COMPONENT, list())

    @property
    def cache_path(self):
        # type: () -> str
        """ Path of the cache component """
        cache_path = self.get_component_path("Alembic")
        if not cache_path:
            cache_path = self.get_component_path("CachePath")
        return cache_path

    @property
    def hda_path(self):
        # type: () -> str
        """ Path of the hda component """
        return self.get_component_path("shared_otls")

    @property
    def thumbnail_url(self):
        # type: () -> str
        """ The thumbnail url of the asset version """
        thumbnail_url = self.asset_version["thumbnail_url"]["url"]
        if thumbnail_url.endswith("img/thumbnail2.png"):
            return str()
        return thumbnail_url

    @property
    def version_num(self):
        # type: () -> int
        """ The current asset version number """
        return self.asset_version['version']

    @property
    def is_latest(self):
        # type: () -> bool
        """ Whether the version is the latest published """
        return bool(self.version_num == self.latest_version_num)

    @property
    def task(self):
        # type: () -> ftrack_api.entity.task
        """ Task of the asset build """
        return self.asset_version['task']

    @property
    def task_name(self):
        # type: () -> str
        """ Name of the task the asset version is under """
        return self.asset_version['task']['name']

    @property
    def asset_build(self):
        # type: () -> ftrack_api.entity.assetbuild
        """ Asset build of the asset version """
        return self.task['parent']

    @property
    def asset_build_name(self):
        # type: () -> str
        """ Asset build type name """
        return self.task['parent']['name']

    @property
    def task_id(self):
        # type: () -> str
        """ Task asset id """
        return self.task['id']

    @property
    def asset_build_type_name(self):
        # type: () -> str
        """
        The asset build type name: e.g. "Character"
        """
        prefix = self.asset_build_name[:2]
        prefix_dict = {v: k for k, v in core_constants.BUILD_MAPPINGS.items()}
        return prefix_dict[prefix]

    @property
    def episode(self):
        # type: () -> ftrack_api.entity.episode
        """
        The episode on ftrack
        """
        return self.sequence['parent']

    @property
    def episode_name(self):
        # type: () -> str
        """ The episode name """
        return self.sequence['parent']['name']

    @property
    def sequence(self):
        # type: () -> ftrack_api.entity.sequence
        """ Sequence object on ftrack """
        return self.shot['parent']

    @property
    def sequence_name(self):
        # type: () -> str
        """ Name of the sequence """
        return self.shot['parent']['name']

    @property
    def shot_name(self):
        # type: () -> str
        """ Name of the shot """
        return self.task['parent']['name']

    @property
    def shot(self):
        # type: () -> ftrack_api.entity.shot
        """ Shot of the asset version """
        return self.task['parent']

    @property
    def shot_id(self):
        # type: () -> str
        """ Name of the shot """
        return self.task['parent']['id']

    @property
    def version_padded(self):
        # type: () -> str
        """ The version in text string with padding of 3 """
        return self.get_version_number_padded(self.asset_version)

    @property
    def version_int(self):
        # type: () -> int
        """ Version number as an integer """
        return self.asset_version['version']

    @property
    def full_shot_name(self):
        # type: () -> str
        """ Get the full shot name """
        shot_name = f"{self.sequence_name}_{self.shot_name}"
        if self.episode_name:
            shot_name = f"{self.episode_name}_{shot_name}"
        return shot_name

    @property
    def category(self):
        # type: () -> str
        """
        The asset version category
        """
        return self.asset_version["asset"]['type']['name']

    @property
    def is_valid(self):
        # type: () -> bool
        """
        Property to show if the status is valid
        and not in an ignored status

        Returns:
            True is the status is valid
        """
        return self.is_version_valid(self.asset_version)

    @property
    def is_camera(self):
        # type: () -> bool
        """
        Check if the asset version is under the camera asset build
        """
        return bool(self.asset_build_type_name == "Camera")

    @property
    def is_build(self):
        # type: () -> bool
        """
        Check if the asset version is an asset build
        """
        shot_prefix = self.asset_build_name.startswith("sh")
        is_digit = self.asset_build_name.isdigit()
        return not shot_prefix and not is_digit

    def add_component_dict(self, name_to_path):
        # type: (dict) -> None
        """
        Add a dictionary of a component name to a file path

        Args:
            name_to_path: Name to file path
        """
        for name, path in name_to_path.items():
            self.add_component(name, path)
        self.session.commit()

    def add_component(self, component_name, file_path):
        # type: (str, str) -> None
        """
        Add a component to the asset version

        Args:
            component_name: Name of the component
            file_path: Path to add
        """
        component = self.asset_version.create_component(file_path,
                                                        location="auto",
                                                        data={"name": component_name}
                                                        )
        self.logger.info(f"Created component {component}")

    def add_playable_component(self, media_path):
        # type: (str) -> None
        """
        Add a movie path to the asset version
        and encode to make it playable

        Args:
            media_path: Path to movie file
        """
        self.asset_version.create_component(
            media_path,
            location="auto",
            data={"name": "Media"}
        )
        self.session.encode_media(
            media_path,
            version_id=self.asset_version_id,
            keep_original=False
        )
        self.session.commit()

    def asset_version_from_path(self, path):
        # type: (str) -> Optional[ftrack_api.entity.asset_version]
        """
        Get a ftrack component from its file path

        Args:
            path: Path of the component to find
        """
        query = f'Component where component_locations any' \
                f' (resource_identifier like "{path}")'
        try:
            component = self.session.query(query).all()[0]
        except (ftrack_api.exception.NoResultFoundError, IndexError):
            return
        return component["version"]

    @property
    def status(self):
        # type: () -> ftrack_api.entity.status
        """ The asset version status """
        return self.asset_version['status']

    @property
    def status_name(self):
        # type: () -> str
        """ Name of the current status """
        return self.status['name']

    @property
    def user_name(self):
        # type: () -> str
        """ Full username with surname """
        first_name = self.asset_version["user"]['first_name']
        last_name = self.asset_version["user"]['last_name']
        user_name = f"{first_name} {last_name}"
        return user_name

    @property
    def asset_type(self):
        # type: () -> str
        """ The asset type of the asset version """
        return self.asset_version["asset"]['type']['name']

    @property
    def version_status(self):
        # type: () -> str
        """ The asset version name """
        return self.asset_version['status']["name"]

    @property
    def comment(self):
        # type: () -> str
        """ The asset version comment """
        return self.asset_version['comment']

    @property
    def created_by(self):
        # type: () -> str
        """ Who created the asset version """
        return self.asset_version["custom_attributes"]["created_by"]

    @property
    def username(self):
        # type: () -> str
        """ Get the asset version username it was published under """
        query = f"User where id is {self.asset_version['user_id']}"
        user = self.session.query(query).one()
        return user["username"]

    @property
    def publish_time(self):
        # type: () -> str
        """
        The time the asset version was published
        """
        time_date = self.asset_version["date"]
        return time_date.format('YYYY-MM-DD HH:mm')

    @property
    def components(self):
        # type: () -> list[ftrack_api.entity.component]
        """
        Get all the asset version components
        """
        return self.asset_version["components"]

    def get_component_path(self, name):
        # type: (str) -> ftrack_api.entity.component
        """
        From the current asset version get the component name

        Args:
            name: Name of the component to find

        Returns:
            component_path_clean: Main ftrack component path clean
        """
        for component in self.asset_version["components"]:
            if component['name'] != name:
                continue
            component_path_clean = file_utils.path_from_component(component)
            return component_path_clean

    @property
    def component_to_path(self):
        # type: () -> dict
        """
        Build a dictionary of component names to its paths
        """
        component_to_path = dict()
        for component in self.asset_version["components"]:
            name = component["name"]
            component_path_clean = self.component_path_clean(component)
            if component_path_clean:
                component_to_path[name] = component_path_clean
        return component_to_path

    @property
    def master_component_path(self):
        # type: () -> str
        """ Get the Master file component """
        return self.get_component_path("MasterFile")

    @property
    def fbx_component_path(self):
        # type: () -> str
        """ Get the FBX file component """
        return self.get_component_path("FBX")

    @property
    def media_component_path(self):
        # type: () -> str
        """ Get the shader file component """
        return self.get_component_path("Media")

    @property
    def metadata_component_path(self):
        # type: () -> str
        """ Get the scene data file component """
        return self.get_component_path("Metadata")

    @property
    def usd_component_path(self):
        # type: () -> str
        """ Get USD file component """
        return self.get_component_path("USD")

    @property
    def materialx_component_path(self):
        # type: () -> str
        """ Get materialx file component """
        return self.get_component_path("MaterialX")

    @property
    def gif_component_path(self):
        # type: () -> str
        """ Get the gif file component """
        return self.get_component_path("GifPath")

    @property
    def matdesc_component_path(self):
        # type: () -> str
        """ Get the Master file component """
        return self.get_component_path("MaterialDescription")

    @property
    def has_playable_component(self):
        # type: () -> bool
        """ Does the playable component exist on the asset version """
        if self.get_component_path("ftrackreview-mp4"):
            return True
        return False

    def get_ext_path_dict(self, extension):
        # type: (str) -> dict
        """
        Get a dictionary of the asset versions
        alembic components names to their paths

        Args:
            extension: The file extension

        Returns:
            alembic_paths: Component name to the abc path
        """
        ext_tuple = (extension,)
        alembic_paths = self.get_component_path_dict(ext_tuple)
        return alembic_paths

    def get_sequence_path_dict(self):
        # type: () -> dict
        """
        Get a dictionary of component name to sequences

        Returns:
            renderlayer_paths: Name to sequence path
        """
        ext_tuple = tuple(core_constants.SEQUENCE_TYPES)
        sequence_paths = self.get_component_path_dict(ext_tuple)
        return sequence_paths

    def get_component_path_dict(self, ext_tuple=None):
        # type: (tuple) -> dict
        """
        Get component name to path directory
        based on the file extensions

        Args:
            ext_tuple: The tuple of file extensions

        Returns:
            component_paths: Name of component to the path
        """
        component_paths = dict()
        for component in self.asset_version["components"]:
            path = self.component_path_clean(component)
            if ext_tuple and not path.endswith(ext_tuple):
                continue

            component_paths[component['name']] = path
        return component_paths

    def create_component_for_path(self, source_path, use_version, ftrack_key):
        # type: (str, int, str) -> None
        """
        Create a component with a file path

        Args:
            source_path: The source file path
            use_version: Version number to publish
            ftrack_key: The component name
        """
        ctx = context_utils.get_context_from_path(source_path)
        ctx.use_version = use_version
        if not ctx.is_sequence:
            publish_path = ctx.pub_file_path

            # create directory for the published alembic
            directory = os.path.dirname(publish_path)
            if not os.path.exists(directory):
                self.logger.info(f"Creating directory: {directory}")
                os.makedirs(directory)
            self.logger.info(f"Copying {source_path} to {publish_path}")
            shutil.copy(source_path, publish_path)
        else:
            publish_path = source_path
            if not os.path.exists(publish_path):
                self.logger.info(f"Creating directory: {publish_path}")
                os.makedirs(publish_path)

        self.logger.info(f"Creating component: {ftrack_key}")
        self.add_component_dict({ftrack_key: publish_path})

    def set_asset_version_thumbnail(self, thumbnail_path):
        # type: (str) -> None
        """
        Set an image as the thumbnail

        Args:
            thumbnail_path: Path to set as the thumbnail
        """
        if thumbnail_path:
            self.asset_version.create_thumbnail(thumbnail_path)

    def display_parameters(self, component_name, source_path):
        # type: (str, str) -> collections.OrderedDict
        """
        An ordered dictionary to add the parameters

        Args:
            component_name: Name of the component
            source_path: The source file path

        Returns:
            display_params_dict: Ftrack parameter name to value
        """
        display_params_dict = collections.OrderedDict()
        display_params_dict["ftrack_id"] = self.asset_version_id
        display_params_dict["component"] = component_name
        display_params_dict["file_name"] = os.path.basename(source_path)
        return display_params_dict

    @property
    def version_numbers(self):
        # type: () -> list[str]
        """
        Get a list of asset version numbers in reverse order
        """
        task_id = self.task["id"]
        query = f'AssetVersion where task_id is "{task_id}"'
        try:
            versions = self.session.query(query).all()
        except ftrack_api.exception.NoResultFoundError:
            return list()

        version_numbers = [str(av["version"]).zfill(3) for av in versions]
        version_numbers.sort()
        version_numbers.reverse()
        return version_numbers

    def component_versions(self, component_name):
        # type: (str) -> dict
        """
        Get a dictionary of the component
        to the asset version and number

        Args:
            component_name: Name of the component

        Returns:
            version_numbers: Number to version
        """
        query = f'select version, version.version from Component where name is "{component_name}" ' \
                f'and version.task.name is {self.task_name} ' \
                f'and version.asset.parent.name is {self.shot_name} ' \
                f'and version.asset.parent.parent.name is {self.sequence_name}'
        components = self.session.query(query).all()

        # build the dictionary of the version
        # number to the asset version
        version_numbers = dict()
        for component in components:
            asset_version = component["version"]
            version_num = asset_version["version"]
            version_numbers[version_num] = asset_version
        return version_numbers

    @property
    def as_dict(self):
        # type: () -> dict
        """
        Get the asset version information as a dictionary

        Returns:
            ctx_dict: Asset version as a dictionary
        """
        if self.is_build:
            ctx_dict = {"entity": "build",
                        "asset_build_type_name": self.asset_build_type_name,
                        "asset_build_name": self.asset_build_name,
                        "task_name": self.task_name,
                        "version_num": self.version_num
                        }
        else:
            ctx_dict = {"entity": "shot",
                        "episode_name": self.episode_name,
                        "sequence_name": self.sequence_name,
                        "shot_name": self.shot_name,
                        "task_name": self.task_name,
                        "version_num": self.version_num
                        }
        return ctx_dict

