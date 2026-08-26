""" Class for specifically querying ftrack """

import ftrack_api
from typing import Optional
from ccftrack.shot import FtShot
from ccftrack.asset import FtAsset
import cccore.file_env.context as context
import cccore.file_env.context_utils as context_utils


class FtQuery(FtShot, FtAsset):
    """
    Wrapper for querying and retrieving ftrack shot data
    """
    def __init__(self, input_project=None, session=None, log=True):
        # type: (Optional[str], Optional[ftrack_api.Session], Optional[bool]) -> None
        """
        Wrapper for querying and retrieving ftrack shot data

        Args:
            input_project: Given project name
            session: The ftrack session
            log: True if logging is wanted
        """
        self._is_build = True
        super(FtQuery, self).__init__(input_project=input_project,
                                      session=session,
                                      log=log
                                      )

    @property
    def is_build(self):
        """
        Returns bool True if it's an asset build
        """
        return self._is_build

    @is_build.setter
    def is_build(self, is_build):
        """
        Setter for bool if it's an asset build
        """
        self._is_build = is_build

    def get_shot_components_of_type(self, asset_type, extensions, filter_name=None):
        # type: (str, list[str], Optional[str]) -> list[ftrack_api.entity.component]
        """
        Get a shots renders by its components by
        the file extension and image sequence asset type

        Args:
            asset_type: Text of asset types
            extensions: List of file extensions
            filter_name: Look for specific text

        Returns:
            components: List of sequence components
        """
        # join the resources text for the extensions
        resources = list()
        for ext in extensions:
            resources.append(f'resource_identifier like "%.{ext}"')
        resources_txt = " or ".join(resources)

        # the asset build id
        if self.is_build:
            parent_id = self.asset_build["id"]
        else:
            parent_id = self.shot["id"]
        query = f'Component where version.asset.type.name is "{asset_type}" ' \
                f'and version.asset.parent.id is "{parent_id}" ' \
                f'and component_locations any ({resources_txt})'

        if self.task_name:
            task_id = self.task["id"]
            query += f' and version.task.id is "{task_id}"'

        self.logger.info(query)
        components = self.session.query(query).all()
        if not filter_name:
            return components

        # filter out camera components
        filtered_components = list()
        for comp in components:
            if comp["name"].endswith(filter_name):
                filtered_components.append(comp)
        return filtered_components

    def get_component_to_version_dict(self, component_name, task_id=None, shot_id=None):
        # type: (str, Optional[str], Optional[str]) ->  dict
        """
        List of version numbers of the specific component name

        Args:
            component_name: Version to information
            task_id: The task id on ftrack
            shot_id: The shot id on ftrack

        Returns:
            version_numbers: List of version numbers
        """
        if task_id:
            query = f'Component where version.task.id is "{task_id}" and name is "{component_name}"'
        elif shot_id:
            query = f'Component where version.asset.parent.id is "{shot_id}" and name is "{component_name}"'
        else:
            query = f'Component where name is "{component_name}" and {self.project_is}'

        components = self.session.query(query).all()
        component_to_version_dict = dict()
        for component in components:

            asset_version = component["version"]
            version_num = str(asset_version['version']).zfill(3)
            component_path = self.component_path_clean(component)
            ftrack_id = asset_version["id"]
            task_id = asset_version["task"]["id"]

            component_to_version_dict[version_num] = {
                "component_path": component_path, "ftrack_id": ftrack_id, "task_id": task_id
            }
        sorted_dict = dict(sorted(component_to_version_dict.items(), key=lambda item: item[0]))
        return sorted_dict

    def version_from_component_and_number(self, task_id, component_name, version_num):
        # type: (str, str, str) ->  ftrack_api.entity.asset_version
        """
        List of version numbers of the specific component name

        Args:
            task_id: The task id on ftrack
            component_name: Name of the component
            version_num: The version number to find

        Returns:
            asset_version: The found asset version
        """
        query = f'Component where version.task.id is "{task_id}" and ' \
                f'version.version is {version_num} and name is "{component_name}"'
        component = self.session.query(query).one()
        return component["version"]

    def get_shot_component_data(self, shot_id):
        # type: (str) -> list[ftrack_api.entity.component]
        """
        From a shot id get the components

        Args:
            shot_id: THe shot to get components for

        Returns:
            components: The shot components
        """
        query = f'select name, file_type, version, version.task, component_locations, ' \
                f'component_locations.resource_identifier, version.asset.type.name from Component ' \
                f'where version.asset.parent.id is "{shot_id}"'
        components = self.session.query(query).all()
        return components

    @property
    def render_component_name_to_data(self):
        """
        Get the sequence camera component name to its data.

        Returns:
            component_name_to_data (dict): Name to path
        """
        components = self.get_shot_components_of_type("Image Sequence", ["exr", "png"])
        return self.component_name_to_data(components)

    @property
    def abc_camera_component_name_to_data(self):
        # type: () -> dict
        """
        Get the alembic camera component name to its data.

        Returns:
            component_name_to_data: Name to path
        """
        components = self.get_shot_components_of_type("Scene", ["abc"], filter_name="CAM")
        return self.component_name_to_data(components)

    @property
    def otls_camera_component_name_to_data(self):
        # type: () -> dict
        """
        Get the otls camera component name to its data.

        Returns:
            component_name_to_data: Name to path
        """
        components = self.get_shot_components_of_type("Scene", ["cpio"], filter_name="OTLS")
        return self.component_name_to_data(components)

    def component_name_to_data(self, shot_to_component):
        # type: (list) -> dict
        """
        Get the component name to its data. Example:
            component_name_to_data["FG"] = {
            "path": "/path/to/the/file.exr",
             "version": 4,
            "asset_version_id": d41a1bab-7bc0-46a1-abbb-ebf447cdcb2e
            }

        Args:
            shot_to_component: List of sequence components

        Returns:
            component_name_to_data: Name to data
        """
        component_name_to_data = dict()
        for component in shot_to_component:

            # get data from components
            asset_version = component["version"]
            version_num = asset_version['version']
            asset_version_id = component["version"]["id"]
            task = asset_version["task"]["name"]
            path = self.component_path_clean(component)
            name = component["name"]

            # build the data dictionary
            data = {"path": path,
                    "version": version_num,
                    "asset_version_id": asset_version_id,
                    "task": task
                    }

            # add to the main dictionary
            if name in component_name_to_data:
                component_name_to_data[name].append(data)
            else:
                component_name_to_data[name] = [data]
        return component_name_to_data

    def is_version_published(self, ctx, category=None):
        # type: (context.Context, Optional[str]) -> bool
        """
        From a context check if its version exists on ftrack
        and return a boolean True if it is

        Args:
            ctx: A set context class
            category: The asset type like "Scene" or "Image Sequence"

        Returns:
            True if the version is found
        """
        version_nums = self.published_version_numbers_from_ctx(
            ctx, category=category)
        if not version_nums:
            return False
        return int(ctx.version) in version_nums

    def published_version_numbers_from_ctx(self, ctx, category=None):
        # type: (context.Context, Optional[str]) -> Optional[list[int]]
        """
        Get a list of published version numbers from its context

        Args:
            ctx: A set context class
            category: The asset type like "Scene" or "Image Sequence"

        Returns:
            All version numbers in order
        """
        query = f"AssetVersion where task.name is {ctx.task} and {self.project_is} "
        if ctx.is_build:
            query += f"and asset.parent.name is {ctx.asset_build} "
        else:
            query += f"and asset.parent.name is {ctx.shot} " \
                     f"and asset.parent.parent.name is {ctx.sequence}"

        if category:
            query += f' and asset.type.name is "{category}"'

        avs = self.session.query(query).all()
        if not avs:
            return None
        version_nums = [int(av['version']) for av in avs]
        version_nums.sort()
        return version_nums

    def latest_version_from_ctx(self, ctx, category=None):
        # type: (context.Context, Optional[str]) -> int
        """
        From a context class get the latest version number

        Args:
            ctx: A set context class
            category: The asset type like "Scene" or "Image Sequence"

        Returns:
            The latest version number
        """
        version_nums = self.published_version_numbers_from_ctx(
            ctx, category=category)
        if not version_nums:
            return 0
        return version_nums[-1]

    def next_version_from_ctx(self, ctx, category=None):
        # type: (context.Context, Optional[str]) -> int
        """
        The next available version number

        Args:
            ctx: A set context class
            category: The asset type like "Scene" or "Image Sequence"

        Returns:
            The next version number
        """
        next_version = self.latest_version_from_ctx(ctx, category=category)
        next_version += 1
        return next_version

    def get_correct_version(self, write_path):
        # type: (str) -> int
        """
        From the write path get the version and compare if
        to the ftrack version and if it's not the same then
        use the highest for the version and write path

        Args:
            write_path: Current write path

        Returns:
            use_version: The next version number to use
        """
        self.logger.info("Confirm the version is correct...")
        ctx = context_utils.get_context_from_path(write_path)

        # compare the next ftrack version with the set version
        next_ftrack_version = self.next_version_from_ctx(ctx)
        if ctx.next_sequence_version == next_ftrack_version:
            self.logger.info(f"Correct version {next_ftrack_version}")
            return next_ftrack_version

        # set the next ftrack version
        use_version = max(next_ftrack_version, ctx.next_sequence_version)
        self.logger.info(f"Updated version sequence path to use {use_version}")
        return use_version

    def component_from_path(self, path):
        # type: (str) -> Optional[ftrack_api.entity.component]
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
        return component

    def get_latest_component_version(self, shot_id):
        # type: (str) -> list[ftrack_api.entity.component]
        """
        From a shot id get a list of a components latest version

        Args:
            shot_id: The shot id to find components for

        Returns:
            latest_component_version: List of latest components
        """
        components = self.get_shot_component_data(shot_id)
        component_name_to_versions = dict()
        latest_component_version = dict()

        for component in components:
            # get the component path version
            component_name = component["name"]
            path = self.component_path_clean(component)
            if not path:
                continue
            version = context_utils.get_context_from_path(path).version

            # get all component versions already found
            versions = component_name_to_versions.get(component_name, list())
            versions.append(version)
            versions.sort()

            # re-add the updated versions to dictionary
            component_name_to_versions[component_name] = versions
            # override the latest version in the dictionary
            if version == max(versions):
                latest_component_version[component_name] = component
        return list(latest_component_version.values())

    def get_hda_metadata_dict(self, project_name=None):
        # type: (Optional[str]) -> dict
        """
        Get the hda name to its metadata

        Args:
            project_name: Name of the project to check

        Returns:
            hda_metadata_dict: The hda name to metadata
        """
        project_name = project_name or self.project_name
        query = f'Project where full_name is "{project_name}"'
        project = self.session.query(query).one()
        project_id = project["id"]

        query = f'select metadata, version, asset.parent.name from ' \
                f'AssetVersion where asset.type.short is "HDA" and project.id is {project_id}'

        hda_metadata_dict = dict()
        asset_versions = self.session.query(query).all()
        for asset_version in asset_versions:

            # get the metadata dictionary in readable format
            metadata_dict = dict()
            for key, value in asset_version["metadata"].items():
                metadata_dict[key] = value

            asset_name = asset_version["asset"]["parent"]["name"]
            hda_metadata_dict[asset_name] = metadata_dict

        return hda_metadata_dict

    @property
    def hda_metadata_dict(self):
        # type: () -> dict
        """ Both the library and project HDA dictionaries """
        hda_metadata_library_dict = self.get_hda_metadata_dict(project_name="Library")
        hda_metadata_project_dict = self.get_hda_metadata_dict()
        hda_metadata_project_dict.update(hda_metadata_library_dict)
        return hda_metadata_project_dict

    @property
    def ingested_tracking_asset_versions(self):
        # type: () -> list[ftrack_api.AssetVersion]
        """ List of ingest data asset versions on project """
        query = (f'select id from AssetVersion where asset.type.name is "Ingest Data" '
                 f'and task.name is "tracking" and {self.project_is}')
        return self.session.query(query).all()

    @property
    def projects_with_new_ingests(self):
        # type: () -> list[ftrack_api.Project]
        """ Projects where there is new ingested plates """
        query = 'Project where custom_attributes any (key is "new_ingest" and value is True)'
        return self.session.query(query).all()

    def get_shot_source_plates(self, shot_id):
        # type: (str) -> Optional[str]
        """
        From the shot id get the source plates exr path

        Args:
            shot_id: The ftrack shot id

        Returns:
            component_path_clean: The clean path of the plates
        """
        query = (f'AssetVersion where asset.type.name is "Ingest Data"'
                 f' and task.name is "source" and asset.parent.id is "{shot_id}"')
        asset_versions_list = self.session.query(query).all()
        if not asset_versions_list:
            return
        for component in asset_versions_list[-1]["components"]:
            component_path_clean = self.component_path_clean(component)
            if component_path_clean and component_path_clean.endswith(".exr"):
                return component_path_clean


