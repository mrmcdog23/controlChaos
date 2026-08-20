""" managing ftrack shots wrapper """
import os
import ftrack_api
import collections
from typing import Optional, Union, Any
import cccore.core_constants as core_constants
import cccore.context as context
from ccftrack.base import FtBase


class FtShot(FtBase):
    """
    Wrapper for querying and retrieving ftrack shot data
    """
    def __init__(self, input_project=None, session=None, log=True):
        # type: (Optional[str], Optional[ftrack_api.Session], Optional[bool]) -> None
        """
        Args:
            input_project: Name of the project to set to
            session: Ftrack session connection
            log: Whether to run the logger
        """
        self._episode_name = None
        self._sequence_name = None
        self._shot_name = None
        self._task_name = None
        super(FtShot, self).__init__(input_project=input_project,
                                     session=session,
                                     log=log
                                     )

    @property
    def episode_names(self):
        # type: () -> list[str]
        """ Get a list of all episode names on the project """
        query = f'select name from Episode where {self.project_is}'
        episodes = self.session.query(query).all()
        return self.get_names(episodes)

    def create_episode(self, episode_name):
        # type: (str) -> None
        """
        Create episode name on ftrack

        Args:
            episode_name: Name of the episode to add
        """
        if episode_name in self.episode_names:
            self.logger.info(f"Episode found on ftrack {episode_name}")
            return
        self.logger.info(f"Creating episode {episode_name}")

        # create episode using data
        episode_dict = {"name": episode_name, "parent": self.project}
        new_episode = self.session.create('Episode', episode_dict)

        self.session.commit()
        return new_episode

    @property
    def episode(self):
        # type: () -> ftrack_api.entity
        """ Get the ftrack episode from the name """
        if not self.episode_name:
            return
        query = f'Episode where name is "{self.episode_name}" and {self.project_is}'
        return self.session.query(query).one()

    @property
    def episode_name(self):
        # type: () -> str
        """ Get episode name """
        return self._episode_name

    @episode_name.setter
    def episode_name(self, episode_name):
        # type: (str) -> None
        """
        Set the episode name. Validate its one ftrack

        Args:
            episode_name: The episode name to set
        """
        if not episode_name:
            return
        if self.episode_name == episode_name:
            return

        if episode_name not in self.episode_names:
            self.logger.error(f"Episode name {episode_name} not found")
            return
        self._episode_name = episode_name
        self.logger.info(f"Episode name {episode_name} found")

    @property
    def sequence_names(self):
        # type: () -> list[str]
        """
        Sequence names from the project
        """
        if self.episode:
            episode_id = self.episode["id"]
            e = self.episode["name"]
            query = f"select name from Sequence where parent.id is {episode_id}"
        else:
            query = f"select name from Sequence where {self.project_is}"
        sequences = self.session.query(query).all()
        return self.get_names(sequences)

    @property
    def sequence_name(self):
        # type: () -> str
        """
        Get sequence name
        """
        return self._sequence_name

    @sequence_name.setter
    def sequence_name(self, sequence_name):
        # type: (str) -> None
        """
        Set the sequence name. Validate its one ftrack

        Args:
            sequence_name: The sequence name to set
        """
        if not sequence_name:
            return
        if sequence_name not in self.sequence_names:
            self.logger.error(f"Sequence name {sequence_name} not found")
            return
        self._sequence_name = sequence_name
        self.logger.info(f"Sequence name {sequence_name} found")

    @property
    def sequence(self):
        # type: () -> ftrack_api.entity.sequence
        """ The current sequence name in ftrack form """
        if self.episode:
            episode_id = self.episode["id"]
            query = f"Sequence where parent.id is {episode_id} and name is {self.sequence_name}"
        else:
            query = f'Sequence where name is "{self.sequence_name}" and {self.project_is}'

        # fix bug where there is the same sequence suffixed
        sequences = self.session.query(query).all()
        if len(sequences) == 1:
            return sequences[0]

        # loop through and find the matching name
        for sequence in sequences:
            if sequence["name"] == self.sequence_name:
                return sequence

    def get_sequence_id(self, sequence_name):
        # type: (str) -> str
        """
        Get the id of a sequence from its name

        Args:
            sequence_name: Name of the sequence to get the id for

        Returns:
            sequence_id: The sequence id
        """
        if self.episode:
            episode_id = self.episode["id"]
            query = f"select id, name from Sequence where parent.id is {episode_id} and name is {sequence_name}"
        else:
            query = f'select id, name from Sequence where name is {sequence_name} and {self.project_is}'
        try:
            sequences = self.session.query(query).all()
        except ftrack_api.exception.NoResultFoundError:
            raise ftrack_api.exception.NoResultFoundError(query)

        if self.episode:
            # fix for ftrack api bug
            for seq in sequences:
                if seq["name"] == sequence_name:
                    return seq.get("id")

        sequence_id = sequences[0].get("id")
        return sequence_id

    def get_shot_names(self, sequence_name, episode_name=None):
        # type: (str, Optional[str]) -> list[str]
        """
        Get a list of shot names from the sequence name

        Args:
            sequence_name: Name of the sequence to get shots of
            episode_name: The episode name to filter

        Returns:
            List of shot names in the sequence
        """
        shots = self.get_shots(sequence_name, episode_name=episode_name)
        return self.get_names(shots)

    def get_shots(self, sequence_name, episode_name=None):
        # type: (str, Optional[str]) -> list[ftrack_api.entity.shot]
        """
        Get a list of shots from the sequence name

        Args:
            sequence_name: Name of the sequence to get shots of
            episode_name: The episode name to filter

        Returns:
            List of shots in the sequence
        """
        if not sequence_name:
            return list()
        if episode_name:
            self.episode_name = episode_name

        sequence_id = self.get_sequence_id(sequence_name)
        query = f'Shot where parent.id is {sequence_id} and {self.project_is}'
        shots = self.session.query(query).all()
        return shots

    @property
    def shot_names(self):
        # type: () -> list[str]
        """ Get a list of shot names """
        sequence_id = self.sequence["id"]
        query = f'select name from Shot where parent.id is {sequence_id} and {self.project_is}'
        shots = self.session.query(query).all()
        return self.get_names(shots)

    def get_shot_id(self, sequence_name, shot_name):
        # type: (str, str) -> Optional[str]
        """
        Get the shot id from the shot name

        Args:
            shot_name: Name of the shot
            sequence_name: Sequence name of the shot

        Returns:
            shot_id: The shot id
        """
        sequence_id = self.get_sequence_id(sequence_name)
        query = f'Shot where parent.id is {sequence_id} and name is {shot_name}'
        try:
            shot = self.session.query(query).all()
        except ftrack_api.exception.NoResultFoundError:
            return None
        for s in shot:
            if s["name"] == shot_name:
                return s.get("id")

    @property
    def shot_id(self):
        # type: () -> str
        """
        Get the current shot id
        """
        return self.shot.get("id")

    @property
    def shot_name(self):
        # type: () -> str
        """
        Get shot name
        """
        return self._shot_name

    @shot_name.setter
    def shot_name(self, shot_name):
        # type: (str) -> None
        """
        Set the shot name. Validate its one ftrack

        Args:
            shot_name: The shot name to set
        """
        if not shot_name:
            return
        if shot_name not in self.get_shot_names(self.sequence_name, episode_name=self.episode_name):
            self.logger.error(f"Shot name {shot_name} not found")
            self._shot_name = None
            return
        self._shot_name = shot_name
        self.logger.info(f"Shot name {shot_name} found")

    @property
    def shot(self):
        # type: () -> ftrack_api.entity.shot
        """
        The current shot name in ftrack form
        """
        sequence_id = self.get_sequence_id(self.sequence_name)
        query = (f'Shot where name is "{self.shot_name}" and'
                 f' {self.project_is} and parent.id is "{sequence_id}"')
        return self.session.query(query).one()

    @property
    def is_shot_found(self):
        # type: () -> bool
        """
        Check if the shot is valid
        """
        try:
            shot_found = self.shot
            self.logger.debug(f"Shot found: {shot_found}")
            return True
        except ftrack_api.exception.NoResultFoundError:
            return False

    def get_shot_task_names(self, sequence_name, shot_name):
        # type: (str, str) -> list[str]
        """
        Get the task names from the shot name

        Args:
            sequence_name: Name of the sequence to get the shot
            shot_name: Name of the shot to get the tasks of

        Returns:
            List of task names
        """
        shot_id = self.get_shot_id(sequence_name, shot_name)
        query = f'Task where parent.id is {shot_id}'
        tasks = self.session.query(query).all()
        return self.get_names(tasks)

    def shot_name_id(self, shot_name):
        # type: (str) -> str
        """
        Get the shot id from its name

        Args:
            shot_name: Name of the shot

        Returns:
            shot_id: id of the given shot name
        """
        sequence_id = self.sequence["id"]
        query = (f'Shot where name is {shot_name} and parent.id '
                 f'is {sequence_id} and {self.project_is}')
        try:
            shot = self.session.query(query).one()
            return shot.get("id")

        # fix for but where a shot starts with the same name
        except ftrack_api.exception.MultipleResultsFoundError:
            for shot in self.session.query(query).all():
                if shot["name"] == shot_name:
                    return shot.get("id")

    @property
    def task(self):
        # type: () -> ftrack_api.entity.task
        """
        Get the task from the asset build and task names

        Returns:
            task: The ftrack task found
        """
        if self.override_task:
            return self.override_task
        if not self.task_name:
            return
        name_id = self.shot_name_id(self.shot_name)
        query = f'Task where parent.id is {name_id} and name is "{self.task_name}"'
        task = self.session.query(query).one()
        return task

    @property
    def task_name(self):
        # type: () -> str
        """
        Get task name
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
            self._task_name = None
            self.logger.error("Task name setting to None")
            return

        if task_name not in self.get_shot_task_names(
                self.sequence_name, self.shot_name):
            error_txt = f"Task name {task_name} not found on {self.shot_name}"
            self.logger.error(error_txt)
            self._task_name = None
            return
        self._task_name = task_name
        self.logger.info(f"Task name {task_name} found on asset build")

    def get_shot_num_to_version(self, sequence_name, shot_name, task_name, category):
        # type: (str, str, str, str) -> collections.OrderedDict
        """
        Get a list of version numbers to asset versions dictionary

        Args:
            sequence_name: Name of the sequence
            shot_name: Name of the shot
            task_name: Name of the task
            category: The asset type like "Scene" or "Image Sequence"

        Returns:
            num_to_version_dict: Dictionary in reverse order
        """
        self.sequence_name = sequence_name
        self.shot_name = shot_name
        self.task_name = task_name
        self.category = category
        return self.num_to_version

    def get_shot_asset_version(self, sequence_name, shot_name, task_name, version_num, category=None):
        # type: (str, str, str, str, Optional[str]) -> ftrack_api.entity.asset_version
        """
        Get version from sequence, shot, task and version number

        Args:
            sequence_name: Name of the sequence
            shot_name: Name of the shot
            task_name: Name of the task
            version_num: Version number padded e.g. "001"
            category: The asset type like "Scene" or "Image Sequence"

        Returns:
            The ftrack asset version
        """
        num_to_version = self.get_shot_num_to_version(
            sequence_name,
            shot_name,
            task_name,
            category
        )
        return num_to_version.get(version_num)

    def create_ftrack_project(self, code, name, root, resolution, fps, apps_dict):
        # type: (str, str, str, str, str, dict) -> None
        """
        Create the ftrack project

        Args:
            code: Project code (Should be 3 letter upper case word)
            name: Project name to add
            root: Directory root folder of the project
            resolution: The project resolution
            fps: The number of frames per second
            apps_dict: Application versions of the project
        """
        # Get relevant schema
        query = f'ProjectSchema where name is {core_constants.SCHEMA_NAME}'
        schema = self.session.query(query).first()
        root_dirname = os.path.basename(root)

        # get project code
        ceta_number = name.split("_")[0]
        if ceta_number.isdigit():
            long_code = f"{ceta_number}_{code}"
        else:
            long_code = f"{code}_{name}"

        # Create project
        proj_dict = {
            "name": long_code,
            "full_name": name,
            "project_schema": schema,
            "custom_attributes": {
                "project_fps": fps,
                "resolution": resolution,
                "short_code": code,
                "server_root": os.path.dirname(root)
            },
            'root': root_dirname
        }

        self.logger.info(f"Creating project {proj_dict}")
        project = self.session.create('Project', proj_dict)
        for app_name, version in apps_dict.items():
            self.logger.info(f"Setting {app_name} to version {version}")
            project['custom_attributes'][app_name] = version

        self.session.commit()
        self.logger.info(f"Created project called {name}")

        # set the project name and create episode and folders
        self._project_names = None
        self.project_name = name

        # create folders under the project
        self.create_folder("build", self.project)
        self.logger.info(f"Created {project}")

    def create_sequence(self, sequence_name, episode_name=None):
        # type: (str, str) -> None
        """
        Create episode name on ftrack

        Args:
            sequence_name: Name of the sequence to create
            episode_name: Name of the episode to parent under
        """
        # set the episode name if given
        if episode_name:
            self.episode_name = episode_name

        if sequence_name in self.sequence_names:
            self.logger.info(f"Sequence {sequence_name} already exists")
            return

        # get the parent object either the project or episode
        parent_entity = self.episode if episode_name else self.project
        self.logger.info(f"Creating sequence {sequence_name}")
        self.session.create('Sequence', {'name': sequence_name, 'parent': parent_entity})
        self.session.commit()

    def create_shot(self, shot_name, sequence_name, episode_name=None, start=None, end=None):
        # type: (str, str, Optional[str], Optional[int], Optional[int]) -> None
        """
        Create a shot under a sequence

        Args:
            shot_name: Name of the shot to create
            sequence_name: Name of the sequence to parent it
            episode_name: Name of the episode to create
            start: First frame of the shot
            end: End frame of the shot
        """
        if episode_name:
            self.episode_name = episode_name
        self.sequence_name = sequence_name

        if shot_name in self.shot_names:
            self.logger.warning(f"{shot_name} already exists in {sequence_name}")
            return

        self.logger.info(f"Creating shot {shot_name} on ftrack")

        # start the frame range if not set yet
        start = start or core_constants.DEFAULT_START_FRAME
        end = end or core_constants.DEFAULT_END_FRAME
        self.logger.info(f"Frame range: {start}-{end}")
        create_shot_dict = {'name': shot_name,
                            'parent': self.sequence,
                            "custom_attributes": {"fstart": start,
                                                  "fend": end,
                                                  "handles": core_constants.DEFAULT_HANDLES,
                                                  "created_by": core_constants.USERNAME
                                                  }
                            }

        new_shot = self.session.create('Shot', create_shot_dict)
        self.create_task_template_for_entity("Shot", new_shot)
        self.session.commit()

    @property
    def cache_asset_versions(self):
        # type: () -> list[ftrack_api.entity.asset_version]
        """
        Get all cache versions

        Returns:
            List of cache asset versions
        """
        task_id = self.task["id"]
        query = f'AssetVersion where asset.type.short is "Cache"' \
                f' and task.id is "{task_id}"'
        return self.session.query(query).all()

    @property
    def render_asset_versions(self):
        # type: () -> list[ftrack_api.entity.asset_version]
        """
        Get all render sequence versions

        Returns:
            List of sequence asset versions
        """
        task_id = self.task["id"]
        query = f'AssetVersion where asset.type.name is "Image Sequence"' \
                f' and task.id is "{task_id}"'
        return self.session.query(query).all()

    @property
    def start(self):
        # type: () -> float
        """
        The start frame of the shot
        """
        return int(self.shot['custom_attributes']['fstart'])

    @property
    def end(self):
        # type: () -> float
        """
        The end frame of the shot
        """
        return int(self.shot['custom_attributes']['fend'])

    def set_range(self, new_start=None, new_end=None):
        # type: (Optional[int], Optional[int]) -> None
        """
        Set the frame shot frame range

        Args:
            new_start: New start frame
            new_end: New End frame
        """
        message = f"Setting {self.shot_name} "
        if new_start:
            self.shot['custom_attributes']['fstart'] = new_start
            message += f"Start: {new_start} "

        if new_end:
            self.shot['custom_attributes']['fend'] = new_end
            message += f"End: {new_end}"

        self.session.commit()
        self.logger.info(message)

    @property
    def handles(self):
        """
        The handles of the shot

        Returns:
            float: Shot handles value
        """
        return self.shot['custom_attributes']['handles']

    def set_from_context(self, ctx):
        # type: (context.Context) -> None
        """
        From context set the ftrack variables

        Args:
            ctx: Current context class
        """
        if ctx.episode:
            self.episode_name = ctx.episode
        self.sequence_name = ctx.sequence
        self.shot_name = ctx.shot
        self.task_name = ctx.task

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
        self.episode_name = data.get("episode_name")
        self.sequence_name = data["sequence_name"]
        self.shot_name = data["shot_name"]
        self.task_name = data["task_name"]
        self.status_name = data["status_name"]
        self.category = data.get("category", "Scene")
        self.version = data.get("version_num")
        self.data = data

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
        self.logger.info("Creating asset version.....")
        asset_version = self.publish(
            self.data["comment"],
            self.shot,
            start=self.data.get("start"),
            end=self.data.get("end"),
            version=self.data.get("version_num")
        )
        return asset_version

    def get_shot_sequence_start(self, shot_name):
        # type: (str) -> Union[Optional[int], Any]
        """
        Get the offset start position of a shot in a sequence

        Args:
            shot_name: The shot name to find

        Return:
            offset: The offset of the shot in the sequence
        """
        sequence_id = self.sequence["id"]
        query = (f'select custom_attributes, name from '
                 f'Shot where parent.id is {sequence_id} and {self.project_is}')
        shots = self.session.query(query).all()

        # add together the shot frame ranges to get the sequence offset
        offset = 0
        for shot in shots:
            # if the shot to find matches return the offset
            if shot["name"] == shot_name:
                return offset

            # add the shot range to the offset
            start = shot["custom_attributes"]["fstart"]
            end = shot["custom_attributes"]["fend"]
            offset += end - start
