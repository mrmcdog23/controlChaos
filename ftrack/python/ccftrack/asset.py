""" Wrapper for ftrack assets specific """
import os
import collections
import ftrack_api
from typing import Optional, Any
from ccftrack.base import FtBase
import cccore.core_constants as core_constants


class FtAsset(FtBase):
    """
    Wrapper for querying and retrieving ftrack asset data
    """
    def __init__(self, input_project=None, session=None, log=True):
        # type: (Optional[str], Optional[ftrack_api.Session], Optional[bool]) -> None
        """
        Args:
            input_project: Given project name
            session: The ftrack session
            log: True if logging is wanted
        """
        self._asset_build_dict = dict()
        self._asset_build_type_name = None
        self._asset_build_name = None
        self._task_name = None
        self._status_name = None
        super(FtAsset, self).__init__(input_project=input_project,
                                      session=session,
                                      log=log
                                      )

    @property
    def asset_build_type_name(self):
        # type: () -> str
        """
        Get asset build type

        Returns:
            _asset_build_type_name: The asset build type
        """
        return self._asset_build_type_name

    @asset_build_type_name.setter
    def asset_build_type_name(self, asset_build_type_name):
        # type: (str) -> None
        """
        Set the asset built name. Validate its one ftrack

        Args:
            asset_build_type_name: The asset build type to set
        """
        if not asset_build_type_name:
            return
        if asset_build_type_name not in self.asset_build_types_names:
            self.logger.error(f"Asset build type {asset_build_type_name} not found")
            return
        self._asset_build_type_name = asset_build_type_name
        self.logger.info(f"Asset build type {asset_build_type_name} found")

    @property
    def asset_build_type(self):
        # type: () -> ftrack_api.entity.assetbuild
        """
        From the asset build dictionary get the asset build type

        Returns:
            Type of asset build from its name
        """
        return self.asset_build_dict[self.asset_build_type_name]

    @property
    def asset_build_name(self):
        # type: () -> str
        """
        Get asset build name
        """
        return self._asset_build_name

    @asset_build_name.setter
    def asset_build_name(self, asset_build_name):
        # type: (str) -> None
        """
        Set the asset name. Validate its one ftrack

        Args:
            asset_build_name: The asset build name to set
        """
        if not asset_build_name:
            return
        if asset_build_name not in self.asset_build_names:
            self.logger.error(f"Asset build name {asset_build_name} not found")
            return
        self._asset_build_name = asset_build_name
        self.logger.info(f"Asset build name {asset_build_name} found")

    @property
    def task_name(self):
        # type: () -> str
        """
        The task name as a property
        """
        return self._task_name

    @task_name.setter
    def task_name(self, task_name):
        # type: (str) -> None
        """
        Set the task name. Validate its one ftrack

        Args:
            task_name: The asset build name to set
        """
        if not task_name:
            return

        if task_name not in self.get_asset_build_task_names(self.asset_build_name):
            error_txt = f"Task name {task_name} not found on {self.asset_build_name}"
            self.logger.error(error_txt)
            self._task_name = None
            return
        self._task_name = task_name
        self.logger.info(f"Task name {task_name} found on asset build")

    @property
    def asset_build_types_names(self):
        # type: () -> list[str]
        """
        Get project asset types names from the project schema

        Returns:
            List of project asset type names
        """
        asset_types = self.get_asset_build_types()
        return self.get_names(asset_types)

    def get_asset_build_names(self, asset_type=None):
        # type: (str) -> list[str]
        """
        Get a list of asset build names from the asset type

        Args:
            asset_type: Name of the asset type (e.g: "Character")

        Returns:
            List of asset build names
        """
        if asset_type:
            type_id = self.asset_build_type_id(asset_type)
            query = f'AssetBuild where type.id is {type_id} and project.id is {self.project_id}'
        else:
            query = f'AssetBuild where {self.project_is}'
        asset_builds = self.session.query(query).all()
        return self.get_names(asset_builds)

    @property
    def asset_build_names(self):
        # type: () -> list[str]
        """
        Find all asset build names on the project

        Returns:
            List of the asset build names
        """
        query = f'AssetBuild where project.id is {self.project_id}'
        asset_builds = self.session.query(query).all()
        return self.get_names(asset_builds)

    def asset_build_type_id(self, asset_type):
        # type: (str) -> Optional[str]
        """
        Get the asset type id from its name

        Args:
            asset_type: Name of the asset type ("Character", "Prop")

        Returns:
            type_id: The ftrack id of the asset type
        """
        query = f'Type where name is "{asset_type}"'
        try:
            types = self.session.query(query).one()
        except ftrack_api.exception.NoResultFoundError:
            return None
        type_id = types.get("id")
        return type_id

    def get_asset_build_from_name(self, asset_build_name):
        # type: (str) -> ftrack_api.entity.assetbuild
        """
        Get the asset build on ftrack from its name

        Args:
            asset_build_name: Name of the asset build to find

        Returns:
            asset_name: Ftrack of the asset build
        """
        query = f'AssetBuild where name is {asset_build_name} and {self.project_is}'
        try:
            asset_name = self.session.query(query).one()
        except ftrack_api.exception.NoResultFoundError:
            return None
        return asset_name

    @property
    def asset_build(self):
        # type: () -> ftrack_api.entity.asset
        """
        Get the asset build from the asset name

        Returns:
            asset_build: The asset build found
        """
        if not self.asset_build_name:
            return
        query = (f'AssetBuild where project.id is {self.project_id} '
                 f'and name is {self.asset_build_name}')
        asset_build = self.session.query(query).one()
        return asset_build

    @property
    def task(self):
        # type: () -> ftrack_api.entity.task
        """
        Get the task from the asset build and task names

        Returns:
            task: The ftrack task found
        """
        if not self.asset_build_name:
            return None
        name_id = self.asset_build_name_id(self.asset_build_name)
        query = f'Task where parent.id is {name_id} and name is "{self.task_name}"'
        try:
            task = self.session.query(query).one()
        except ftrack_api.exception.NoResultFoundError:
            return None
        return task

    def asset_build_name_id(self, asset_build_name):
        # type: (str) -> Optional[str]
        """
        Get the asset build id from its name

        Args:
            asset_build_name: Name of the asset build

        Returns:
            asset_build_name_id: id of the given asset build
        """
        asset_name = self.get_asset_build_from_name(asset_build_name)
        if not asset_name:
            return str()
        asset_build_name_id = asset_name.get("id")
        return asset_build_name_id

    def get_asset_build_name_tasks(self, asset_build_name):
        # type: (str) -> list[ftrack_api.entity.task]
        """
        Get all tasks assigned to the asset build name

        Args:
            asset_build_name: Name of the asset build

        Returns:
            List of ftrack tasks
        """
        name_id = self.asset_build_name_id(asset_build_name)
        query = f'Task where parent.id is {name_id}'
        tasks = self.session.query(query).all()
        return tasks

    def get_asset_build_task_names(self, asset_build_name):
        # type: (str) -> list[str]
        """
        From an asset name get all the assigned tasks in name format

        Args:
            asset_build_name: Name of the asset build to find

        Returns:
            List of task names
        """
        tasks = self.get_asset_build_name_tasks(asset_build_name)
        return self.get_names(tasks)

    def get_asset_task_names(self, asset_build_name):
        # type: (str) -> list[str]
        """
        Get the task names from the asset name

        Args:
            asset_build_name: Name of the asset build to find

        Returns:
            List of task names
        """
        query = f'Task where parent.name is "{asset_build_name}"'
        tasks = self.session.query(query).all()
        return self.get_names(tasks)

    def get_asset_build_task(self, asset_name, task_name):
        # type: (str, str) -> ftrack_api.entity.task
        """
        The asset build task

        Args:
            asset_name: The asset name to find
            task_name: Name of the task to find

        Returns:
            task: The task to find
        """
        name_id = self.asset_build_name_id(asset_name)
        query = f'Task where parent.id is {name_id} and name is "{task_name}"'
        task = self.session.query(query).one()
        return task

    def get_asset_build_num_to_version(self, asset_build_name, task_name, category):
        # type: (str, str, str) -> collections.OrderedDict
        """
        Get a list of version numbers to asset versions dictionary

        Args:
            asset_build_name: Name of the asset build
            task_name: Name of the task
            category: The asset type like "Scene" or "Image Sequence"

        Returns:
            num_to_version: Dictionary in reverse order
        """
        self.asset_build_name = asset_build_name
        self.task_name = task_name
        self.category = category
        return self.num_to_version

    @property
    def project_tag_names(self):
        # type: () -> list[str]
        """ Get a list of the project tags """
        tags = self.session.query('Tag').all()
        return self.get_names(tags)

    def get_build_asset_version(self, asset_build_name, task_name, version_num, category):
        # type: (str, str, str, str) -> ftrack_api.entity.asset_version
        """
        Get version from name, task and version number

        Args:
            asset_build_name: Name of the asset build
            task_name: Name of the task
            version_num: Version number padded e.g. "001"
            category: The asset type like "Scene" or "Image Sequence"

        Returns:
            The ftrack asset version
        """
        num_to_version = self.get_asset_build_num_to_version(
            asset_build_name,
            task_name,
            category
        )
        return num_to_version.get(version_num)

    @property
    def asset_build_dict(self):
        # type: () -> dict
        """
        Build a dictionary of the asset build name to its type

        Returns:
            _asset_build_dict: Name to the build type
        """
        if not self._asset_build_dict:
            for build_type in self.get_asset_build_types():
                self._asset_build_dict[build_type["name"]] = build_type
        return self._asset_build_dict

    def set_from_context(self, ctx):
        # type: (Any) -> None
        """
        From context set the ftrack variables

        Args:
            ctx: Current context class
        """
        self.asset_build_type_name = ctx.build_type
        self.asset_build_name = ctx.asset_build
        self.task_name = ctx.task

    def create_ftrack_asset(self, asset_build_type_name, asset_name):
        # type: (str, str) -> None
        """
        Create a shot under a sequence

        Args:
            asset_build_type_name: Name of the asset build type
            asset_name: Name of the asset to create
        """
        self.logger.info(f"Creating {asset_build_type_name} {asset_name} on ftrack")
        self.asset_build_type_name = asset_build_type_name

        parent_folder = self.get_folder("asset")
        custom = {"created_by": core_constants.USERNAME}
        new_asset_build = self.session.create(
            "AssetBuild", {"name": asset_name,
                           "type": self.asset_build_type,
                           "parent": parent_folder,
                           "custom_attributes": custom
                           }
        )
        self.create_task_template_for_entity(asset_build_type_name, new_asset_build)
        self.session.commit()

    def set_ftrack_data(self, data):
        # type: (dict) -> ftrack_api.entity.asset_version
        """
        Publish an asset from dictionary of values

        Args:
            data: The data of the asset

        Returns:
            asset_version: Published asset version
        """
        self.logger.info("Publishing to Ftrack...")
        self.asset_build_type_name = data["asset_build_type_name"]
        self.asset_build_name = data["asset_build_name"]
        self.task_name = data["task_name"]
        self.status_name = data["status_name"]
        self.category = data.get("category", "Scene")
        self.data = data
        self.version = data.get("version_num")

        if self.data.get("merge_asset_version"):
            self.logger.info("Merging with existing asset version...")
            return self.current_asset_version

        # get next file publish path
        asset_version = self.publish_asset()
        self.copy_and_publish_wip_file(asset_version)
        return asset_version

    def publish_asset(self):
        # type: () -> ftrack_api.entity.asset_version
        """
        From the data publish the asset version

        Returns:
            asset_version: Published asset version
        """
        asset_version = self.publish(self.data["comment"],
                                     self.asset_build,
                                     version=self.data.get("version_num")
                                     )
        return asset_version

    def asset_names_with_task_type(self, task_name):
        # type: (str) -> list[str]
        """
        On the project get a list of all asset anes
        with a published fur asset version

        Args:
            task_name: Name of the task to find assets for

        Returns:
            asset_names: List of asset names with rigs
        """
        # get all tasks ids on the project
        query = f'Task where name is "{task_name}" and project.id is {self.project_id}'
        rig_tasks = self.session.query(query).all()
        id_str = ",".join([task['id'] for task in rig_tasks])

        # get all asset versions with the task ids
        query = f'AssetVersion where task_id in ({id_str})'
        versions = self.session.query(query).all()

        # get all the asset names
        asset_names = set()
        for version in versions:
            asset_names.add(version["task"]["parent"]["name"])
        return list(asset_names)

    def builds_with_asset_type(self, asset_type):
        # type: (str) -> list[str]
        """
        On the project get a list of all asset names
        with a published asset_type  asset version

        Args:
            asset_type: Name of the asset type: "HDA", "Scene"...

        Returns:
            asset_names: List of asset names with rigs
        """
        query = f'AssetVersion where asset.type.short is "{asset_type}"'
        versions = self.session.query(query).all()
        asset_builds = list()
        for version in versions:
            if version['project_id'] == self.project_id:
                asset_builds.append(version["task"]["parent"])
        return asset_builds

    @property
    def start(self):
        # type: () -> int
        """ The start frame of the asset """
        return 1

    @property
    def end(self):
        # type: () -> int
        """ The end frame of the asset  """
        return 1
