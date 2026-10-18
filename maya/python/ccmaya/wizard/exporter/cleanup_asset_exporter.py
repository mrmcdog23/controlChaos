""" Asset publisher in maya """
import os
import sys
import shutil
import tempfile
import maya.cmds as cmds
import maya.mel as mel
from ccgeneral.wizard.exporter.base_exporter import BaseExporter
import cccore.file_env.context as context
import cccore.utils.file_utils as file_utils
import ccmaya.maya_constants as maya_constants


# initialize maya standalone
try:
    import maya.standalone
    maya.standalone.initialize()
except (TypeError, RuntimeError):
    pass


class CleanupAssetExporter(BaseExporter):
    def __init__(self):
        super().__init__()
        self.groups_list = list()

    def export(self):
        """
        Export the asset and publish it to FTrack
        """
        self.load_fbx_file()
        self.create_geo_group()
        self.create_joints_group()
        self.remove_redundant_top_level_nodes()
        self.save_master_file()
        self.export_fbx_file()
        self.publish_shot()

    @property
    def is_rig(self):
        # type: () -> bool
        """ If there are joints then it is a rig not a mesh """
        return bool(cmds.ls(type="joint"))

    def load_fbx_file(self):
        """
        Load the fbx plugin and the fbx file
        """
        self.log(f"Asset publish complete: {self.data}")
        if not cmds.pluginInfo("fbxmaya", query=True, loaded=True):
            cmds.loadPlugin("fbxmaya")

        # import the fbx file
        fbx_file_path = self.data["fbx_file_path"]
        self.log(f"Importing fbx file: {fbx_file_path}")
        cmds.file(fbx_file_path, i=True)

    def create_geo_group(self):
        """
        Group all the meshes
        """
        num_of_meshes = len(cmds.ls(type="mesh"))
        self.log(f"Grouping {num_of_meshes} meshes...")
        geo_grp = cmds.group(cmds.ls(type="mesh"), n=maya_constants.GEO_GRP)
        geo_grp_world = cmds.parent(geo_grp, w=True)[0]
        self.groups_list.append(geo_grp_world)

    def create_joints_group(self):
        """
        If it is a rig then group the joints
        """
        if not self.is_rig:
            self.logger.warning("No joints found")
            return

        joints = cmds.ls(type="joint", l=True)
        self.log(f"Grouping {len(joints)} joints...")

        root_joint = None
        for joint in joints:

            # get the root joint node to group
            parent_node = cmds.listRelatives(joint, p=True, f=True)
            if not parent_node:
                root_joint = joint
                break

            # get the root node if there no parent
            if cmds.objectType(parent_node[0]) != "joint":
                root_joint = joint
                break

        # group and unparent
        joint_grp = cmds.group(root_joint, n=maya_constants.JNT_GRP)
        joint_grp_world = cmds.parent(joint_grp, w=True)[0]
        self.groups_list.append(joint_grp_world)

    def remove_redundant_top_level_nodes(self):
        """
        Remove any nodes not in groups
        """
        ignore_nodes = maya_constants.DEFAULT_CAMERAS
        ignore_nodes.extend(self.groups_list)
        ignore_nodes_tuple = tuple(ignore_nodes)
        self.logger.info(f"Ignore nodes: {ignore_nodes_tuple}")

        # delete all nodes that are not top level
        for node in cmds.ls(assemblies=True):
            if node.endswith(ignore_nodes_tuple):
                continue
            self.logger.info(f"Removing node: {node}")
            cmds.delete(node)

        # group nodes
        if self.is_rig:
            cmds.group(self.groups_list, n=maya_constants.RIG_GRP)

    def save_master_file(self):
        """
        Save the master maya file
        """
        self.ctx = context.Context(overrides=self.data)
        self.ctx.use_ext = "ma"
        next_version = self.ftquery.get_correct_version(self.ctx)
        self.logger.info(f"Using next version number: {next_version}")
        self.ctx.use_version = next_version

        master_file_path = self.ctx.save_file_path
        file_utils.create_directories(master_file_path)

        cmds.file(rename=master_file_path)
        cmds.file(save=True, type='mayaAscii')
        self.additional_components["master_file_path"] = master_file_path
        self.data["version_num"] = next_version

    def export_fbx_file(self):
        """
        Export the asset and publish it to FTrack
        """
        for node in cmds.ls(assemblies=True):
            is_rig_grp = maya_constants.RIG_GRP in node
            is_geo_grp = maya_constants.GEO_GRP in node
            if is_rig_grp or is_geo_grp:
                cmds.select(node)
                break

        # get the fbx file export path
        fbx_asset_path = self.ctx.fbx_file_path
        file_utils.create_directories(fbx_asset_path)
        self.logger.info(f"Export fbx file: {fbx_asset_path}")

        # export the fbx file
        # Reset to defaults, then configure
        mel.eval("FBXResetExport")
        mel.eval("FBXExportFileVersion -v FBX202000")   # match your target app
        mel.eval("FBXExportInAscii -v false")           # binary is smaller/faster
        mel.eval("FBXExportUpAxis y")                   # y or z
        mel.eval("FBXExportSmoothingGroups -v true")
        mel.eval("FBXExportSmoothMesh -v false")
        mel.eval("FBXExportSkins -v true")
        mel.eval("FBXExportShapes -v true")             # blendshapes
        mel.eval("FBXExportCameras -v false")
        mel.eval("FBXExportLights -v false")
        mel.eval("FBXExportEmbeddedTextures -v false")
        mel.eval("FBXExportBakeComplexAnimation -v false")
        mel.eval(f'FBXExport -f "{fbx_asset_path}" -s')
        self.additional_components["FBX"] = fbx_asset_path
        self.log(f"Export FBX path: {fbx_asset_path}")


if __name__ == "__main__":
    exporter = CleanupAssetExporter()
    exporter.batch_process(sys.argv[1])
