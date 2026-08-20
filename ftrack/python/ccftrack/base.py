""" Base ftrack wrapper for general functions """
import os
import operator
import collections
import ftrack_api
import shutil
from typing import Any, Optional
import cccore.utils.file_utils as file_utils
import cccore.utils.cc_logging as cc_logging
import cccore.core_constants as core_constants
import cccore.data.server_data as server_data


class ResultsError(ftrack_api.exception.NoResultFoundError):
    """ Exception when results query aren't found """
    pass


class FtBase(object):
    """
    Base class for ftrack connection and session
    """
    def __init__(self, input_project=None, session=None, log=True):
        # type: (Optional[str], Optional[ftrack_api.Session], Optional[bool]) -> None
        """
        Args:
            input_project: Name of the project to set to
            session: Ftrack session connection
            log: Whether to run the logger
        """
        super(FtBase, self).__init__()
        self.input_project = input_project
        self._session = session
        self._project_name = None
        self._project_names = list()
        self._project = None
        self._is_episodic = None
        self._asset_version = None
        self._version_number = None
        self._status_name = None
        self._category = None
        self.override_task = None
        self.version = None
        self.data = dict()
        self.server_data = server_data.ProjectData()
        self.logger = cc_logging.cc_logger()
        self.logger.disabled = not log

        # begin the ftrack session.
        self.session = session
        self.set_project(session)

    def set_project(self, session):
        # type: (ftrack_api.Session) -> None
        """
        Get the input project and set the project. If none was
        given use the environment or revert ot first project.
        If there was a session passed in it means the project
        is already set and there is no need to set it

        Args:
            session: The ftrack session
        """
        if session:
            self.project_name = self.server_data.project_name
            return

        if self.input_project:
            self.logger.info(f"Using given project name {self.input_project}")
            self.project_name = self.input_project

        if not self.project_name:
            env_project_name = self.server_data.project_name
            if env_project_name:
                self.logger.info(f"Project environment: {env_project_name}")
                self.project_name = env_project_name

        # if no project still not set then use the first one on ftrack
        if not self.project_name:
            self.project_name = self.projects_names[0]
            self.logger.info(f"No project found using first on Ftrack: {self.project_name}")

    @property
    def project_name(self):
        # type: () -> str
        """ Return the project name """
        return self._project_name

    @project_name.setter
    def project_name(self, project_name):
        # type: (str) -> None
        """
        Set the project name. Validate its on ftrack
        """
        if project_name not in self.projects_names:
            self.logger.info(f"Project name {project_name} not found")
            return
        self._project = None
        self._project_name = project_name
        self.logger.debug(f"Set project to {project_name}")

    @property
    def active_projects(self):
        # type: () -> list[ftrack_api.entity.project]
        """
        Get all project listed on ftrack that are active

        Returns:
            active_projects: List of ftrack projects
        """
        all_projects = self.session.query('Project').all()
        active_projects = list()
        for project in all_projects:
            if project["status"] == "active":
                active_projects.append(project)
        return active_projects

    @property
    def all_project_codes(self):
        # type: () -> list[ftrack_api.entity.project]
        """
        Get all project codes listed on ftrack
        """
        all_projects = self.session.query('select name from Project').all()
        return self.get_names(all_projects)

    @property
    def all_project_short_codes(self):
        # type: () -> list[ftrack_api.entity.project]
        """
        Get all project long codes listed on ftrack
        """
        all_projects = self.session.query('select name from Project').all()
        short_codes = [proj["custom_attributes"]["short_code"] for proj in all_projects]
        short_codes.sort()
        return short_codes

    @property
    def root(self):
        # type: () -> str
        """
        Root of the project set on Ftrack. Use the project name
        and not the directory as the directory has a limit
        """
        return self.project["full_name"]

    @staticmethod
    def get_names(data):
        # type: (list[dict]) -> list[str]
        """
        From a list of dictionaries get the name key

        Args:
            data: List of dictionaries

        Returns:
            names: List of names from the data
        """
        names = [a["name"] for a in data]
        names.sort()
        return names

    @property
    def projects_code(self):
        # type: () -> list[str]
        """ Get a list of all project codes on ftrack """
        return self.get_names(self.get_active_projects)

    @property
    def project_code(self):
        # type: () -> str
        """ Project code. Three character upper case """
        return self.project["name"]

    @property
    def project_short_code(self):
        # type: () -> str
        """ Project long code. Cata and three character upper case """
        return self.project["custom_attributes"]["short_code"]

    @property
    def projects_names(self):
        # type: () -> list[str]
        """
        Get a list of all project names on ftrack.
        Filter names that start with digits
        """
        if self._project_names:
            return self._project_names

        self._project_names = [a["full_name"] for a in self.active_projects]
        self._project_names.sort()
        self._project_names.reverse()
        return self._project_names

    @property
    def project_code_to_name(self):
        # type: () -> dict
        """
        Dictionary of project code to its name
        """
        project_code_to_name_dict = dict()
        query = "select name, full_name from Project"
        all_projects = self.session.query(query).all()
        for project in all_projects:
            project_code_to_name_dict[project["name"]] = project["full_name"]
        return project_code_to_name_dict

    @property
    def projects_names_no_lib(self):
        # type: () -> list[str]
        """ List of ftrack project names no lib """
        projects_names = self.projects_names
        for lib_project in [core_constants.LIBRARY, core_constants.FX_LIBRARY]:
            if lib_project in projects_names:
                projects_names.remove(lib_project)
        return projects_names

    @property
    def session(self):
        # type: () -> ftrack_api.Session
        """ Session property """
        return self._session

    @session.setter
    def session(self, session=None):
        # type: (Optional[ftrack_api.Session]) -> None
        """
        Get the session. Connect if not already set

        Returns:
            self._session: Ftrack session
        """
        if session:
            self._session = session
        else:
            api_user = "contact@control-chaos.com"

            self.logger.info(f"Connecting to ftrack as {api_user}")
            API_KEY = "NTE0Y2JhYWQtNzZiNS00ODlkLTg3N2EtNDExZDZkODA1ZTAwOjphNGQ4ZTA0MS0yZDNlLTQ3NDgtYWNjMC04YjgxOTQwYWE0MTY"
            SERVER_URL = "https://control-chaos.ftrackapp.com/"
            self._session = ftrack_api.Session(server_url=SERVER_URL,
                                               api_key=API_KEY,
                                               api_user=api_user
                                               )

    @property
    def project(self):
        # type: () -> ftrack_api.entity.project
        """ Get the ftrack project """
        if not self._project:
            query = f'Project where full_name is "{self.project_name}"'
            self._project = self.session.query(query).first()
        return self._project

    @property
    def project_id(self):
        # type: () -> str
        """ Ftrack id of the project """
        return self.project.get("id")

    @property
    def project_is(self):
        # type: () -> str
        """ Get text to filter for the project id """
        return f"project.id is {self.project_id}"

    def commit(self):
        """
        Commit changes to ftrack
        """
        self.session.commit()

    @property
    def is_commercial(self):
        # type: () -> bool
        """ Is the project a commercial project """
        project_type = self.project["custom_attributes"]["project_type"][0]
        return project_type == core_constants.COMMERCIAL

    @property
    def is_longform(self):
        # type: () -> bool
        """ Is the project a commercial project """
        project_type = self.project["custom_attributes"]["project_type"][0]
        return project_type == core_constants.LONGFORM

    @property
    def usernames(self):
        # type: () -> list[str]
        """ Get a list of usernames """
        usernames_list = list()
        for user in self.session.query("User").all():
            usernames_list.append(user["username"])
        usernames_list.sort()
        return usernames_list

    @property
    def username(self):
        # type: () -> str
        """ The api username """
        return self.session.api_user

    @property
    def user(self):
        # type: () -> ftrack_api.entity.user
        """ The current ftrack user """
        query = f'User where username is "{self.username}"'
        return self.session.query(query).one()

    @property
    def is_admin(self):
        # type: () -> bool
        """ Does the current user have admin rights """
        admin = "Administrator"
        for role in self.user["user_security_roles"]:
            if role["security_role"]["name"] == admin:
                return True
        return False

    @property
    def is_creator(self):
        # type: () -> bool
        """ Is the user a creator """
        creator = "Creator"
        for role in self.user["user_security_roles"]:
            if role["security_role"]["name"] == creator:
                return True
        return False

    @property
    def category(self):
        # type: () -> str
        """ Return the asset type """
        return self._category

    @category.setter
    def category(self, category):
        # type: (str) -> None
        """ Set the asset type """
        self._category = category

    @property
    def schema(self):
        # type: () -> dict
        """ The current project schema """
        return self.project["project_schema"]

    def get_task_type(self, task_name):
        # type: (str) -> ftrack_api.entity.task_type
        """
        Get the task type from its name

        Args:
            task_name: Name of the task to find

        Returns:
            task_type: Ftrack task type
        """
        task_type_schema = self.schema["task_type_schema"]
        for task_type in task_type_schema["types"]:
            if task_name == task_type["name"]:
                return task_type

    def add_task_to_entity(self, entity, task_name):
        # type: (ftrack_api.entity.assetbuild, str) -> None
        """
        Add the task of a name to an entity

        Args:
            entity: Asset build to use as parent
            task_name: Name of the task to create
        """
        task_type = self.get_task_type(task_name)
        if not task_type:
            self.logger.error(f"Task name {task_name} not found in schema")
            return
        self.session.create('Task', {'name': task_name,
                                     'parent': entity,
                                     'type': task_type
                                     })

        self.session.commit()
        self.logger.info(f"Created task {task_name} on {entity}")

    def create_task_name_on_entity(self, task_name, entity):
        # type: (str, Any) -> ftrack_api.entity.task
        """
        Create a task name on an asset or shot.

        Args:
            task_name: The task name to create
            entity: Parent either the AssetBuild or Shot

        Return:
            task_created: The newly created task
        """
        task = self.get_task_type(task_name)
        if not task:
            raise TypeError(f"Task name {task_name} not found on FTrack")

        task_created = self.create_task_on_entity(task, entity)
        self.session.commit()
        return task_created

    def create_task_on_entity(self, task_type, entity):
        # type: (ftrack_api.entity.task, Any) -> None
        """
        Create a task on an asset or shot. This will be
        done by giving the entity as the parent and the task
        type as the ftrack task.

        Args:
            task_type: The ftrack task to create
            entity: Parent either the AssetBuild or Shot
        """
        task_type_name = task_type["name"]
        entity_name = entity["name"]
        message = f"Creating task {task_type_name} for {entity_name}..."
        self.logger.info(message)

        task_create_dict = {'name': task_type_name,
                            'parent': entity,
                            'type': task_type
                            }
        task_created = self.session.create('Task', task_create_dict)
        return task_created

    def create_task_template_for_entity(self, entity_type, entity):
        # type: (str, ftrack_api.entity.assetbuild) -> None
        """
        Create all the tasks for the shot based on the project schema template

        Args:
            entity_type: Name of the entity type ("Shot", "Prop", "Vehicle")
            entity: Asset build to use as parent
        """
        task_types = self.get_entity_task_types(entity_type)
        for task_type in task_types:
            self.create_task_on_entity(task_type, entity)
        self.session.commit()

    def create_edit_task(self, edit_folder, task_name):
        # type: (ftrack_api.entity.folder, str) -> ftrack_api.entity.task
        """
        Create the task under the edit folder for flame exports

        Args:
            edit_folder: Parent folder to create the task under
            task_name: Name of the task folder to create

        Returns:
            task: Entity created for the task
        """
        edit_folder_id = edit_folder["id"]
        query = f'Task where name is "{task_name}" and parent.id is {edit_folder_id}'
        try:
            return self.session.query(query).one()
        except ftrack_api.exception.NoResultFoundError:
            self.logger.info(f"No task named {task_name} found")
        task = self.create_task_name_on_entity(task_name, edit_folder)
        self.logger.info(f"Created sequence: {task}")
        return task

    @property
    def all_avaliable_tasks(self):
        # type: () -> list[ftrack_api.entity.type]
        """
        List of all avaliable tasks on ftrack
        """
        avaliable_tasks = []
        for task in self.session.query("Type"):
            name = task["name"]
            if name.islower():
                avaliable_tasks.append(task)
        return avaliable_tasks

    @property
    def all_avaliable_task_names(self):
        # type: () -> str
        """
        Get a list of all ftrack task names
        """
        return self.get_names(self.all_avaliable_tasks)

    def create_folder(self, name, parent):
        # type: (str, Any) -> ftrack_api.entity.folder
        """
        Create folder on Ftrack

        Args:
            name: Name of the folder to create
            parent: Parent of the folder

        Returns:
            folder: The newly created ftrack folder
        """
        folder_dict = {'name': name, 'parent': parent}
        folder = self.session.create('Folder', folder_dict)
        self.logger.info(f"Creating {name} on Ftrack")
        self.commit()
        return folder

    def get_asset_build_types(self):
        # type: () -> list[dict]
        """
        Get all asset types from the project schema

        Returns:
            List of project asset types
        """
        return self.schema.get_types('AssetBuild')

    def get_entity_task_types(self, entity_type):
        # type: (str) -> list[str]
        """
        Get a list of tasks that are assigned to asset
        build type in the project schema

        Args:
            entity_type: Name of the entity type ("Shot", "Prop", "Vehicle")

        Returns:
            asset_type_task_list: List of task names
        """
        task_types = list()
        for task_template in self.schema['task_templates']:
            if task_template["name"] != entity_type:
                continue
            for task_data in task_template["items"]:
                task_type = task_data["task_type"]
                task_types.append(task_type)
        return task_types

    def get_entity_task_types_names(self, entity_type):
        # type: (str) -> list[str]
        """
        Get a list of task names that are assigned to asset
        build type in the project schema

        Args:
            entity_type: Name of the entity type ("Shot", "Prop", "Vehicle")

        Returns:
            List of task names for the entity type
        """
        task_types = self.get_entity_task_types(entity_type)
        return self.get_names(task_types)

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

    def build_names_in_schema(self, schema_name):
        # type: (str) -> list[str]
        """
        Get asset types names from a given project schema name

        Args:
            schema_name: Name of the project schema

        Returns:
            List of schema asset type names
        """
        query = f'ProjectSchema where name is {schema_name}'
        schema = self.session.query(query).first()
        asset_types = schema.get_types('AssetBuild')
        return self.get_names(asset_types)

    def get_folder(self, name):
        # type: (str) -> ftrack_api.entity.folder
        """
        The project folder from the name

        Args:
            Name of the ftrack folder to find

        Returns:
            The ftrack folder of the name
        """
        query = f'Folder where name is "{name}" and parent.id is {self.project_id}'
        try:
            child_tasks = self.session.query(query)
            folder = child_tasks.one()
        except ftrack_api.exception.NoResultFoundError:
            raise ResultsError(f"Folder {name} not found")
        return folder

    @property
    def asset_folder(self):
        # type: () -> ftrack_api.entity.folder
        """
        The project asset folder
        """
        return self.get_folder("build")

    @property
    def task(self):
        """
        The current task
        """
        raise NotImplementedError

    @property
    def version_statuses(self):
        # type: () -> list[ftrack_api.entity.Status]
        """
        The project asset version statuses
        """
        return self.schema.get_statuses(schema='AssetVersion')

    @property
    def version_statuses_names(self):
        # type: () -> list[ftrack_api.entity.Status]
        """
        Get a list of the status names
        """
        return self.get_names(self.version_statuses)

    @property
    def task_statuses(self):
        # type: () -> list[ftrack_api.entity.Status]
        """
        The project task statuses
        """
        return self.schema.get_statuses(schema='Task')

    @property
    def status_name(self):
        # type: () -> str
        """
        Get the status name
        """
        return self._status_name

    @status_name.setter
    def status_name(self, status_name):
        # type: (str) -> None
        """
        Set the asset built name. Validate its one ftrack

        Args:
            status_name: The status name to set
        """
        if status_name not in self.version_statuses_names:
            self.logger.error(f"Status {status_name} not found on project")
            return
        self._status_name = status_name
        self.logger.info(f"Status {status_name} found")

    @property
    def status(self):
        # type: () -> list[ftrack_api.entity.Status]
        """
        The status on ftrack from its name
        """
        query = f'Status where name is "{self.status_name}"'
        status = self.session.query(query).one()
        return status

    def get_asset(self, parent, name):
        # type: (Any, str) -> ftrack_api.Asset
        """
        Check ftrack for the asset exists

        Args:
            parent: Ftrack.Shot or Ftrack.Asset to use as parent of the asset
            name: Name of the asset to use

        Returns:
            asset: The asset as it exists on ftrack
        """
        parent_id = parent.get("id")
        query = f'Asset where name is "{name}" and parent.id is {parent_id}'
        self.logger.info(query)
        assets = self.session.query(query)
        if not assets.all():
            self.logger.warning("No asset exists of this type")
            return

        for asset in assets.all():
            if asset["type"]["name"] == self.category:
                asset_name = asset.get("name")
                self.logger.info(f"Found asset name: {asset_name}")
                return asset
        self.logger.warning("Asset type not found")

    def find_or_create_asset(self, parent, use_name=None):
        # type: (Any, str) -> ftrack_api.entity.asset
        """
        Check ftrack for the current asset and if it doesn't exist create it

        Args:
            parent: Ftrack.Shot or Ftrack.Asset to use as parent of the asset
            use_name: Name of the asset to use

        Returns:
            asset: The asset as it exists on ftrack
        """
        name = use_name or self.task['name']
        asset = self.get_asset(parent, name)
        if asset:
            return asset

        # create if it doesn't exist
        shot_type_query = f'AssetType where name is "{self.category}"'
        self.logger.info(shot_type_query)
        shot_type = self.session.query(shot_type_query).one()
        self.logger.info(shot_type)
        asset_dict = {'name': name,
                      'parent': parent,
                      'type': shot_type,
                      'task': self.task
                      }
        asset = self.session.create('Asset', asset_dict)
        asset_name = asset.get("name")
        self.logger.info(f"Creating asset: {asset_name}")
        return asset

    def create_ftrack_asset_version(self, asset, comments, parent, version=None, commit=False):
        # type: (Any, str, Any, Optional[int], Optional[bool]) -> ftrack_api.asset_version
        """
        Create an asset version on ftrack

        Args:
            asset: The asset as it exists on ftrack
            comments: Publish the given maya file
            parent: Ftrack.Shot or Ftrack.Asset parent of the asset
            version: The number of the version
            commit: Whether to commit to ftrack

        Returns:
            asset_version: Created asset version
        """
        custom_attributes = {"created_by": core_constants.USERNAME}
        wip_file_path = self.data.get("wip_file_path")
        if wip_file_path:
            custom_attributes["wip_file_path"] = wip_file_path

        asset_version_dict = {
            "asset": asset,
            "comment": comments,
            "parent": parent,
            "custom_attributes": custom_attributes
        }
        if self.task:
            asset_version_dict['task'] = self.task

        if version:
            if self.latest_version_num >= version:
                self.logger.warning(f"No version number {version} too low.")
            else:
                self.logger.info(f"Version Number given to use: {version}")
                asset_version_dict["version"] = version
        else:
            self.logger.info(f"No version number given.")

        asset_version = self.session.create('AssetVersion', asset_version_dict)
        self.logger.info(f"Created asset version: {asset_version}")

        if commit:
            self.session.commit()
        return asset_version

    def publish(self, comments, parent, start=None, end=None, version=None):
        # type: (str, Any, Optional[int], Optional[int], Optional[int]) -> ftrack_api.asset_version
        """
        Publish the file path along with comments and status

        Args:
            comments: Publish the given maya file
            parent: Ftrack.Shot or Ftrack.Asset parent of the asset
            start: Start frame
            end: End frame
            version: The number of the version

        Returns:
            asset_version: Created asset version
        """
        self.category = self.data.get("category", "Scene")
        self.logger.info(f"Category type: {self.category}")
        asset = self.find_or_create_asset(parent)
        self.logger.info(f"Found asset: {asset}")
        asset_version = self.create_ftrack_asset_version(
            asset, comments, parent, version=version)

        # set the status if given
        if self.status:
            asset_version['status'] = self.status

        # set the metadata
        metadata = self.data.get("metadata")
        if start and end:
            metadata = {"start": start, "end": end}
        asset_version["metadata"] = metadata

        # attach the thumbnail
        thumbnail_path = self.data.get("thumbnail_path")
        if thumbnail_path:
            if os.path.exists(thumbnail_path):
                asset_version.create_thumbnail(thumbnail_path)
                asset_version['task'].create_thumbnail(thumbnail_path)
            else:
                self.logger.critical(f"Path does not exist: {thumbnail_path}")
        self.commit()

        self.logger.info(f"Version number: {asset_version['version']}")
        self.data["version_num"] = asset_version["version"]
        return asset_version

    @property
    def asset_versions(self):
        # type: () -> list[ftrack_api.entity.asset_version]
        """
        Get a list of asset versions in reverse order
        """
        if not self.task:
            return list()
        task_id = self.task['id']
        query = f'AssetVersion where task_id is "{task_id}"'
        if self.category:
            query += f' and asset.type.name is "{self.category}"'
        try:
            versions = self.session.query(query).all()
        except ftrack_api.exception.NoResultFoundError:
            return list()
        sorted_versions = sorted(versions, key=operator.itemgetter('version'), reverse=True)
        return sorted_versions

    @property
    def category_names(self):
        # type: () -> list[str]
        """
        Asset version types: e.g. ["HDA", "Scene"]

        Returns:
            asset_version_categories: List of types
        """
        self.category = None
        version_categories = set()
        for version in self.asset_versions:
            version_type = version["asset"]["type"]["name"]
            version_categories.add(version_type)
        asset_version_categories = list(version_categories)
        asset_version_categories.sort()
        return asset_version_categories

    @staticmethod
    def get_version_number_padded(version):
        # type: (ftrack_api.entity.asset_version) -> str
        """
        From the ftrack version convert to a padded number string

        Args:
            version: Version in ftrack form

        Returns:
            version_text: The padded version with v at start
        """
        version_num_padded = str(version['version']).zfill(3)
        return version_num_padded

    @property
    def num_to_version(self):
        # type: () -> collections.OrderedDict
        """
        Dictionary of the version in text to the ftrack version

        Returns:
            num_to_version_dict: Dictionary in reverse order
        """
        num_to_version_dict = collections.OrderedDict()
        for version in self.asset_versions:
            version_text = self.get_version_number_padded(version)
            num_to_version_dict[version_text] = version
        return num_to_version_dict

    @property
    def latest_asset_version(self):
        # type: () -> Optional[ftrack_api.entity.asset_version]
        """
        Get the latest published asset version
        """
        versions = self.asset_versions
        for version in versions:
            if self.is_version_valid(version):
                return version
        return None

    @property
    def current_asset_version(self):
        # type: () -> Optional[ftrack_api.entity.asset_version]
        """
        Get the current published asset version
        """
        find_version_num = self.data["version_num"]
        versions = self.asset_versions
        for version in versions:
            if self.is_version_valid(version):
                if find_version_num == version["version"]:
                    return version
        self.logger.warning(f"Version {find_version_num} not found!")
        return None

    @staticmethod
    def is_version_valid(asset_version):
        # type: (ftrack_api.entity.asset_version) -> bool
        """
        Check if the asset version status is valid

        Args:
            asset_version: Check the asset version is valid status

        Returns:
            True if the status is not in an ignore status
        """
        status_name = asset_version["status"]['name']
        return bool(status_name not in core_constants.IGNORE_STATUSES)

    @property
    def latest_version_num(self):
        # type: () -> int
        """
        The latest version number of the published asset
        """
        latest_version = self.latest_asset_version
        if not latest_version:
            return 0
        return self.latest_asset_version['version']

    @property
    def next_asset_version_num(self):
        # type: () -> int
        """
        Next published asset version number
        """
        return self.latest_version_num + 1

    def copy_and_publish_wip_file(self, asset_version):
        # type: (ftrack_api.entity.asset_version) -> None
        """
        Get the wip path and work out the published
        path and copy it to the correct location

        Args:
            asset_version: The asset version to add to
        """
        wip_file_path = self.data.get("wip_file_path")
        pub_file_path = self.data.get("pub_file_path")
        if not wip_file_path and not pub_file_path:
            self.logger.warning("No wip or publish file path given")
            return

        # copy the wip file to the published file
        if wip_file_path and not pub_file_path:
            self.logger.info(f"WIP file path: {wip_file_path}")
            ctx = context_utils.get_context_from_path(wip_file_path)
            ctx.use_version = self.data["version_num"]
            pub_file_path = ctx.pub_file_path
            self.logger.info(f"FTrack publish path: {pub_file_path}")

            file_utils.create_directory(os.path.dirname(pub_file_path))
            shutil.copy(wip_file_path, pub_file_path)
            self.data["pub_file_path"] = pub_file_path

        # if the wip and publish are the same nothing to copy
        if wip_file_path == pub_file_path:
            self.logger.info("WIP path will be the published file")

        # if no publish file has been acquired
        if not pub_file_path:
            self.logger.warning("No publish file path found")
            return

        # create the master file component
        component = asset_version.create_component(pub_file_path,
                                                   location='auto',
                                                   data={"name": "MasterFile"}
                                                   )
        self.logger.info(f"Created component {component}")
        self.commit()

    def get_asset_version_from_number(self, version_number):
        # type: (str) -> ftrack_api.entity.asset_version
        """
        From a number get the asset version of the current task

        Args:
            version_number: The version number to find

        Returns:
            asset_version: Found version on ftrack
        """
        task_id = self.task['id']
        query = (f'AssetVersion where task_id is "{task_id}" '
                 f'and version is {version_number}')
        asset_version = self.session.query(query).one()
        return asset_version

    @property
    def app_versions(self):
        # type: () -> dict
        """
        Application versions on the project

        Returns:
            The current projects application versions
        """
        app_versions = dict()
        attributes = self.project['custom_attributes']
        for app in list(core_constants.APP_VERSION.keys()):
            versions = attributes[app]
            try:
                use_version = versions[0]
            except IndexError:
                use_version = None
            app_versions[app] = use_version
        return app_versions

    @property
    def resolution(self):
        # type: () -> Optional[list[int]]
        """
        The current projects frames per second
        """
        resolution = self.project['custom_attributes']["resolution"]
        if not resolution:
            return None
        width, height = resolution.split("x")
        return [int(width), int(height)]

    @property
    def fps(self):
        # type: () -> float
        """ The current projects frames per second """
        return float(self.project['custom_attributes']["project_fps"][0])

    @property
    def new_ingest(self):
        # type: () -> float
        """ The current projects frames per second """
        return self.project['custom_attributes']["new_ingest"]

    @new_ingest.setter
    def new_ingest(self, new_ingest):
        # type: (str) -> None
        """
        Set the project name. Validate its on ftrack
        """
        self.project['custom_attributes']["new_ingest"] = new_ingest
        self.commit()

    @property
    def nuke_version(self):
        # type: () -> str
        """ The nuke version of the project """
        return self.app_versions[core_constants.NUKE]

    @property
    def houdini_version(self):
        # type: () -> str
        """ The houdini version of the project """
        return self.app_versions[core_constants.HOUDINI]

    @staticmethod
    def component_path_clean(component):
        # type: (ftrack_api.entity.component) -> str
        """
        Get the component path

        Args:
            The component to get the path

        Returns:
            File path of the component
        """
        return file_utils.path_from_component(component)


