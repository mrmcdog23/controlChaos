""" Build an ingested scene """
import hou
import sys
import os
from PIL import Image
from typing import Optional, Any
import cchoudini.utils.hou_utils as hou_utils
import cchoudini.utils.node_utils as node_utils
import ccftrack.asset as asset
import ccftrack.query as query
import ccftrack.asset_version as asset_version
import cccore.utils.cc_logging as cc_logging
import cccore.utils.sequence_utils as sequence_utils
import cccore.utils.file_utils as file_utils
import cccore.file_env.context as context
import cchoudini.node.ftrack_hou_node as ftrack_hou_node


# constants
CATEGORY_TO_COLOUR = {
    "Tracking Bundle": hou.Color(0.8, 0.9, 0.1),
    "Cache": hou.Color(0.5, 0.0, 0.7),
    "Scene": hou.Color(0.5, 0.7, 0.1)
}


class BuildHoudiniScene(object):
    """
    Build the houdini scene from the tracking bundle
    """
    def __init__(self,
                 asset_version_id,  # type: str
                 session,  # type: Any
                 component_to_path=None,  # type: Optional[dict]
                 save=False,  # type: Optional[bool]
                 xpos=None,  # type: Optional[int]
                 ypos=None,  # type: Optional[int]
                 count=None,  # type: Optional[int]
                 load_hda=True  # type: Optional[bool]
                 ):
        """
        Args:
            asset_version_id: The asset version id to add to
            session: Ftrack session connection
            component_to_path: Component to path dictionary
            save: Whether to save the scene
            xpos: The starting x position for the nodes
            ypos: The starting y position for the nodes
        """
        self.ypos = ypos or 0
        self.xpos = xpos or 0
        self.count = count or 0
        self.save = save
        self.load_hda = load_hda
        self.ftver = asset_version.FtAssetVersion(session=session)
        self.ftasset = asset.FtAsset(session=self.ftver.session)
        self.ftquery = query.FtQuery(session=self.ftver.session)
        self.ftver.asset_version_id = asset_version_id
        self.component_to_path = component_to_path or self.ftver.component_to_path

        self.logger = cc_logging.cc_logger()
        self.shot_nodes = list()
        self.camera_nodes = list()
        self.ud_plate_path = str()
        self.scene_data = dict()

    def create_scene(self):
        """
        Create the tracking scene
        """
        self.import_sequence_caches()
        self.set_viewport_camera()
        self.set_undistort_plate()
        self.save_hip_and_add_to_asset_version()

    def get_asset_data(self, alembic_path):
        # type: (str) -> Optional[dict]
        """
        Loop through all assets and see if the alembic is in the data

        Args:
            alembic_path: Path of the alembic file

        Returns:
            asset_data: The found asset data
        """
        for namespace, asset_data in self.scene_data.items():
            if alembic_path == asset_data["abc_path"]:
                return asset_data

    def import_lookdev(self, component_name, source_path):
        # type: (str, str) -> Optional[hou.Node]
        """
        Try and find and import the lookdev into the scene
        if there is one via the exported metadata

        Args:
            component_name: Name of the component
            source_path: Path of the alembic to import

        Returns:
            The new hda node
        """
        if not self.load_hda:
            return

        if "_cam" in source_path.lower():
            self.logger.warning(f"Asset type is camera so no lookdev")
            return

        self.logger.info(f"Loading lookdev for path: {source_path}")
        self.logger.info(f"asset_version_id: {self.ftver.asset_version_id}")

        # check if the asset is in the metadata
        asset_data = self.get_asset_data(source_path)
        if not asset_data:
            self.logger.warning(f"Not found asset data for {component_name}")
            return

        # if it is a camera then there is no lookdev
        if asset_data["asset_build_type_name"] == "Camera":
            self.logger.warning(f"Asset type is camera so no lookdev")
            return

        # set the new version to find
        asset_build_name = asset_data["asset_build_name"]
        self.ftasset.asset_build_name = asset_build_name
        self.ftasset.task_name = "lookdev"
        self.ftasset.category = "HDA"

        # if there is no version then skip
        latest_asset_version = self.ftasset.latest_asset_version
        if not latest_asset_version:
            self.logger.warning(f"No lookdev HDA found for {asset_build_name}")
            return

        asset_version_id = self.ftasset.latest_asset_version["id"]
        self.logger.info(f"Found lookdev latest id: {asset_version_id}")
        latest_ftver = asset_version.FtAssetVersion(session=self.ftver.session)
        latest_ftver.asset_version_id = asset_version_id

        # load a hda file by getting the definition
        hda_path = latest_ftver.master_component_path
        self.logger.info(f"HDA path: {hda_path}")

        parent_node = hou.node("obj")

        # build shot data dictionary
        shot_data = {
            "shot_task_ftrack_id": self.ftver.task_id,
            "shot_version_ftrack_id": self.ftver.asset_version_id,
            "shot_cache_path": source_path,
            "shot_cache_name": os.path.basename(source_path),
            "shot_version": self.ftver.version_padded
        }
        hda_node = node_utils.load_published_hda(
            parent_node,
            latest_ftver,
            component_name,
            latest_ftver.master_component_path,
            shot_data
        )

        # add the ftrack parameters to the main node
        self.shot_nodes.append(hda_node)
        # set the abc path
        return hda_node

    def import_alembic(self, component_name, source_path):
        # type: (str, str) -> hou.Node
        """
        create the alembic node and component

        Args:
            component_name: Name of the ftrack component
            source_path: Path of the source file

        Returns:
            alembic_node: The newly created alembic node
        """

        # reading metadata of the scene
        # check if the asset is in the metadata
        asset_data = self.get_asset_data(source_path) or dict()

        # if it is a camera then there is no lookdev
        if not asset_data:
            filename = os.path.basename(source_path)
            is_camera = "cam" in filename.lower()
        else:
            is_camera = asset_data.get("asset_build_type_name") == "Camera"

        if is_camera:
            self.logger.info(f"Loading alembic the camera...")
            main_node = hou.node("/obj").createNode(
                "alembicarchive", component_name)
            main_node.parm("fileName").set(source_path)
            main_node.parm("buildHierarchy").pressButton()

            # find all camera nodes if there are any
            cam_nodes = hou_utils.find_all_subnodes_of_types(main_node, ["cam"])
            self.camera_nodes.extend(cam_nodes)

        else:
            # direct file load
            main_node = hou.node("/obj").createNode(
                "geo", f"{component_name}_abc")
            alembic_node = main_node.createNode(
                "alembic", f"{component_name}_abc")
            alembic_node.parm("fileName").set(source_path)

        # work out the index of the current version
        ftnode = ftrack_hou_node.FTrackHouNode(main_node)
        ftnode.component_name = component_name
        ftnode.source_path = source_path
        ftnode.version_padded = self.ftver.version_padded

        if asset_data:
            ftnode.asset_build_type_name = asset_data["asset_build_type_name"]
            ftnode.asset_build_name = asset_data["asset_build_name"]
            ftnode.asset_version_id = asset_data["ftrack_id"]

        ftnode.shot_version_ftrack_id = self.ftver.asset_version_id
        ftnode.shot_task_ftrack_id = self.ftver.task_id
        ftnode.shot_cache_name = os.path.basename(source_path)
        ftnode.shot_cache_path = source_path

        ftnode.asset_cache_path = os.path.basename(source_path)
        ftnode.asset_cache_path = source_path

        ftnode.add_ftrack_parameters()

        # add the ftrack parameters to the main node
        self.shot_nodes.append(main_node)
        return main_node

    def import_fbx(self, component_name, source_path):
        # type: (str, str) -> None
        """
        Import the fbx component and path

        Args:
            component_name: Name of the fbx component
            source_path: Path of the fbx file
        """
        self.logger.critical(f"FBX not yet supported {component_name} {source_path}")

    def set_viewport_camera(self):
        """
        Set the camera viewport from the imported camera
        """
        if not self.camera_nodes:
            return
        camera_path = self.camera_nodes[0].path()
        hou_utils.set_camera_viewport(camera_path)

    def import_cache_sequence(self, component_name, source_path):
        # type: (str, str) -> Optional[hou.Node]
        """
        Import a cache sequence into the scene

        Args:
            component_name: Name of the component to create
            source_path: Path of the cache sequence

        Returns:
            geo_node: The new geometry node
        """
        try:
            seq_data = sequence_utils.get_sequence_data(source_path)
        except FileNotFoundError:
            return
        geo_node = hou.node("/obj").createNode("geo", component_name)
        file_node = geo_node.createNode("file", f"{component_name}_cache")
        file_node.parm("file").set(seq_data.houdini_path)
        self.shot_nodes.append(geo_node)
        return geo_node

    def import_sequence_caches(self):
        """
        Import all the alembic nodes
        """
        self.scene_data = self.ftver.metadata
        for component_name, source_path in self.component_to_path.items():
            node = None

            # look if it's the un-distort plate
            if "ud_plate" in component_name.lower():
                self.logger.info("Found UD Plate")
                self.ud_plate_path = source_path

            # if it's not an alembic node continue
            if source_path.endswith(".abc"):
                node = self.import_lookdev(component_name, source_path)
                if not node:
                    node = self.import_alembic(component_name, source_path)

            elif source_path.endswith((".bgeo.sc", ".vdb")):
                node = self.import_cache_sequence(component_name, source_path)

            elif source_path.endswith(".fbx"):
                self.import_fbx(component_name, source_path)

            # if there is node then position it
            if node:
                self.count += 1
                self.xpos += 2
                node.setPosition((self.xpos, self.ypos))

            # get position the node
            if self.count == 5:
                self.count = 0
                self.ypos -= 1
                self.xpos = 0

    def set_undistort_plate(self):
        """
        Set the undistorted plates on the camera nodes
        """
        if not self.camera_nodes:
            self.logger.critical("No camera nodes imported")
            return

        if not self.ud_plate_path:
            self.logger.critical("No undistorted plate found")
            return

        # setting the plate to all cameras
        self.logger.info(f"Setting camera nodes: {self.camera_nodes}")
        self.logger.info(f"UD Plate: {self.ud_plate_path}")

        # extract the data information for the timeline
        seq_data = sequence_utils.get_sequence_data(self.ud_plate_path)
        self.logger.info(f"Frame range: {seq_data.frame_range}")
        hou.playbar.setFrameRange(seq_data.start, seq_data.end)

        # set the cameras to use the houdini path
        img = Image.open(seq_data.frame_paths[0])
        width, height = img.size
        self.logger.info(f"Plate resolution: {width}x{height}")

        for cam_node in self.camera_nodes:
            cam_node.parm("vm_background").set(seq_data.houdini_path)
            cam_node.parm("resx").set(width)
            cam_node.parm("resy").set(height)
            cam_node.parent().parent().setColor(hou.Color(0.5, 1.0, 0.7))
            self.logger.info(f"Setting camera node: {cam_node.name()}")

    def save_hip_and_add_to_asset_version(self):
        """
        Save the hip file and add it to the asset version
        """
        if not self.save:
            return
        overrides = {"sequence_name": self.ftver.sequence_name,
                     "shot_name": self.ftver.shot_name,
                     "task_name": self.ftver.task_name,
                     "version_num": self.ftver.version_int,
                     "app": "houdini",
                     "ext": "hip"
                     }

        # from the override dictionary work out the
        # file path to save the publishing file
        ctx = context.Context(overrides=overrides)
        pub_file_path = ctx.pub_file_path
        pub_directory = os.path.dirname(pub_file_path)
        file_utils.create_directories(pub_directory)
        hou.hipFile.save(pub_file_path)
        self.logger.info(f"Published path: {pub_file_path}")

        # add component to asset version
        self.ftver.add_component("hipFile", pub_file_path)
        self.logger.info("Completed publish")


if __name__ == "__main__":
    build_scene_inst = BuildHoudiniScene(sys.argv[1], save=True)
    build_scene_inst.create_scene()
