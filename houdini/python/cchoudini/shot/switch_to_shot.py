""" Load or update assets from one houdini scene to another """
import re
import hou
import ftrack_api
from typing import Optional
import ccftrack.shot as shot
import ccftrack.query as query
import cccore.file_env.context as context
import cccore.utils.cc_logging as cc_logging
import cccore.utils.file_utils as file_utils
import cchoudini.utils.node_utils as node_utils
import cchoudini.utils.hou_utils as hou_utils
import cchoudini.utils.shot_override_parm as shot_override_parm
from cchoudini.shot.build_scene import BuildHoudiniScene


class SwitchToShot(object):
    """
    Switch from one houdini scene to another
    """
    shot_info_path = "/obj/shotInfo"
    shot_cam_path = "/obj/shotCam"

    def __init__(self, episode_name, sequence_name, shot_name, task_name, template_file=None, ftshot=None, save=False):
        # type: (str, str, str, str, Optional[str], Optional[ftrack_api.entity], Optional[bool]) -> None
        """
        Args:
            episode_name: The name of the episode
            sequence_name: Sequence name to switch to
            shot_name: Shot name to switch to
            template_file: Source file to use as the template
            ftshot: Ftrack shot instance
            save: Whether of not to save the file
        """
        self.episode_name = episode_name
        self.sequence_name = sequence_name
        self.shot_name = shot_name
        self.task_name = task_name
        self.template_file = template_file
        self.save = save
        self._camera_path = str()
        self.hou_file_path = str()

        # set class variables
        self.components_found_in_scene = list()
        self.logger = cc_logging.cc_logger()
        session = ftshot.session if ftshot else None
        self.ftquery = query.FtQuery(session=session)
        self.ftshot = ftshot or shot.FtShot(session=self.ftquery.session)

        # run setup class
        self.open_template_file()
        self.clean_scene()
        self.set_environment_variables()
        self.swap_or_load_assets()
        self.set_parameter_overrides()
        self.set_shot_frame_range()
        self.set_shot_info_node()
        self.reorganise_nodes()
        self.save_file_path()

    def open_template_file(self):
        """
        Open the template file if one is given
        """
        if not self.template_file:
            return
        self.logger.info(f"Opening {self.template_file}")
        hou.hipFile.load(self.template_file,
                         suppress_save_prompt=True,
                         ignore_load_warnings=True
                         )

    def set_environment_variables(self):
        """
        Set the environment to swap the paths
        """
        hou.hscript(f"set -g EP = {self.episode_name}")
        hou.hscript(f"set -g SEQ = {self.sequence_name}")
        hou.hscript(f"set -g SHOT = {self.shot_name}")

    def clean_scene(self):
        """
        Remove unwanted nodes
        """
        shot_cam_node = hou.node(self.shot_cam_path)
        if shot_cam_node:
            shot_cam_node.destroy()

    def set_shot_frame_range(self):
        """
        Update frame range of the scene
        """
        self.ftshot.sequence_name = self.sequence_name
        self.ftshot.shot_name = self.shot_name
        self.logger.info(f"Setting frame range to {self.ftshot.start}-{self.ftshot.end}")
        hou.playbar.setFrameRange(self.ftshot.start, self.ftshot.end)
        hou.setFrame(self.ftshot.start)

    def set_parameter_overrides(self):
        """
        Set the overrides on the parameters
        """
        self.logger.info(f"Setting parameter overrides...")
        for node in hou.node('/').allSubChildren():
            for parm in node.parms():
                if parm.name().startswith("shotoverride_"):
                    self.logger.info(f"Setting parameter...{parm.name()}")
                    shot_override_parm.set_override_parm_value(parm)

    def swap_or_load_assets(self):
        """
        Swap existing asset paths or create new ones
        """
        self.logger.info("Swapping scene assets and loading new ones...")
        shot_assets = hou_utils.get_shot_assets(session=self.ftshot.session)
        shot_id = self.ftshot.get_shot_id(self.sequence_name, self.shot_name)
        latest_component_version = self.ftquery.get_latest_component_version(shot_id)

        found_shot_assets = list()
        av_to_build_dict = dict()
        for component in latest_component_version:

            # extract the node data of the component
            component_name = component["name"]
            asset_version = component["version"]
            asset_version_id = asset_version["id"]
            task_id = asset_version['task']['id']
            version_padded = str(asset_version['version']).zfill(3)

            # get the component path
            file_path = file_utils.path_from_component(component)
            shot_asset = shot_assets.get(component_name)
            self.logger.info(f"Component name... {component_name}")
            self.logger.info(f"New path: {file_path}")
            if shot_asset:
                # set the new node path and viewport
                self.logger.info(f"Found asset {shot_asset.node_path}")
                shot_asset.switch_version(task_id, asset_version_id, file_path, version_padded)
                found_shot_assets.append(component_name)
            else:
                # build the node if not found in scene
                self.logger.info(f"Creating asset...")
                component_to_path_build = av_to_build_dict.get(asset_version_id, dict())
                component_to_path_build[component_name] = file_path
                av_to_build_dict[asset_version_id] = component_to_path_build

        # hide unneeded shot assets
        shot_assets = hou_utils.get_shot_assets(session=self.ftshot.session)
        for shot_component_name, shot_asset in shot_assets.items():
            if shot_component_name not in found_shot_assets:
                shot_asset.set_invisible()

        # any nodes in the scene from before the swap not found hide
        for asset_version_id, component_to_path_build in av_to_build_dict.items():
            self.logger.info(f"asset_version_id:{asset_version_id}")
            self.logger.info(f"Build data:{component_to_path_build}")
            build_scene_inst = BuildHoudiniScene(
                asset_version_id,
                component_to_path=component_to_path_build,
                session=self.ftshot.session
            )
            build_scene_inst.create_scene()

        self.logger.info(f"Building nodes...")

        # set the camera node
        self.set_shot_camera_viewport()

    @property
    def camera_path(self):
        # type: () -> Optional[str]
        """ Get the correct camera path """
        if self._camera_path:
            return self._camera_path

        # loop through all the published shot assets
        shot_assets = hou_utils.get_shot_assets(session=self.ftshot.session)
        for shot_component_name, shot_asset in shot_assets.items():
            # skip if not visible
            if not shot_asset.is_visible:
                continue

            # check the subnodes for cameras and continue if there aren't any
            camera_nodes = hou_utils.find_all_subnodes_of_types(shot_asset.node, ["cam"])
            if not camera_nodes:
                continue

            # loop through all camera nodes skipping the witness camera
            for camera_node in camera_nodes:
                if "witness" in camera_node.name().lower():
                    continue
                # set the camera path and return
                self._camera_path = camera_node.path()
                return self._camera_path

    def set_shot_camera_viewport(self):
        """
        Set the camera viewport from the node
        """
        if self.camera_path:
            hou_utils.set_camera_viewport(self.camera_path)

    def set_shot_info_node(self):
        """
        Set the data on the shot info node
        """
        if not self.camera_path:
            self.logger.warning("No camera node path found")
            return

        # find the shot info node
        shot_info_node = hou.node(self.shot_info_path)
        if not shot_info_node:
            self.logger.warning("Shot info node not found")
            return

        self.logger.info("Setting shot info node")
        shot_info_node.parm("shotCam").set(self.camera_path)
        camera_node = hou.node(self.camera_path)
        plate_path = camera_node.parm("vm_background").evalAsString()
        shot_info_node.parm("plate").set(plate_path)

    def reorganise_nodes(self):
        """
        Reorganise the remaining nodes
        """
        # remove previous
        episode_names_set = tuple(self.ftshot.episode_names)
        boxes = hou.node("/obj/").findNetworkBoxes("*")
        for box in boxes:
            if box.comment().startswith(episode_names_set):
                self.logger.info(f"Removing network box {box.comment()}")
                box.destroy()

        remaining_nodes = list()
        shot_assets_dict = hou_utils.get_shot_assets(session=self.ftshot.session)

        for shot_asset in list(shot_assets_dict.values()):
            if shot_asset.is_non_deletable:
                continue

            node = shot_asset.node
            # remove hidden nodes
            if not shot_asset.is_visible:
                node.destroy()
            else:
                remaining_nodes.append(node)

        # set the node positions and create the box
        node_utils.set_position_nodes(remaining_nodes)
        box_name = f"{self.episode_name}_{self.sequence_name}_{self.shot_name}"
        hou_utils.create_network_box(
            remaining_nodes, box_name, colour=hou.Color(0.5, 0.0, 0.7)
        )

    def save_file_path(self):
        """
        Save the file path at the end of the build
        """
        if not self.save:
            return
        ctx = context.Context(overrides={
            "episode_name": self.episode_name,
            "sequence_name": self.sequence_name,
            "shot_name": self.shot_name,
            "task_name": self.task_name,
            "ext": "hip"
        })
        self.hou_file_path = ctx.next_wip_save_path
        self.logger.info(f"Saved Houdini path: {self.hou_file_path}")
        hou.hipFile.save(file_name=self.hou_file_path)
