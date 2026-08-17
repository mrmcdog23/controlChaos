""" Fbx animation exporter from Maya """
import maya.cmds as cmds
import pymel.core as pm
import cccore.utils.file_utils as file_utils
import cccore.utils.cc_logging as cc_logging
import ccmaya.asset.scene_asset as scene_asset


class FbxAnimExport(object):
    """
    Export fbx files from a given list of namespaces to the cache directory
    """
    def __init__(self, namespaces, save_dir):
        # type: (str, str) -> None
        """
        Args:
            namespaces: Namespaces to export
            save_dir: Directory to export the fbx file to
        """
        self.start = int(cmds.playbackOptions(q=True, ast=True))
        self.end = int(cmds.playbackOptions(q=True, aet=True))
        self.namespaces = namespaces
        self.save_dir = save_dir
        self.logger = cc_logging.cc_logger()

        # initialize the class variables
        self.objects_to_bake = list()
        self.namespace_to_fbx_path = dict()
        self.namespace_to_objects = dict()

    def run_fbx_exports(self):
        """
        run the export functions
        """
        self.setup_scene_for_fbx()
        self.add_camera_for_bake()
        self.bake_fbx_nodes()
        self.export_fbx_files()

    def setup_scene_for_fbx(self):
        """
        Setup the scene for fbx exporting
        """
        self.logger.info(f"Unparent joints for baking: {self.namespaces}")
        for namespace in self.namespaces:
            scene_asset_inst = scene_asset.SceneAsset(namespace)

            # store objects to export
            if scene_asset_inst.cam_grp:
                self.namespace_to_objects[namespace] = [scene_asset_inst.cam_grp]
                self.logger.info(f"Camera node {namespace} so no joints will be found")
                continue

            # if there is no
            if not scene_asset_inst.geo_grp:
                self.logger.info(f"No geo group found on {namespace}")
                continue

            # check the root joint exists on the asset
            root_joint = scene_asset_inst.root_joint
            if not root_joint:
                self.logger.error(f"Not root joint found for {namespace}")
                self.namespace_to_objects[namespace] = [scene_asset_inst.geo_grp]
                continue

            # import if referenced object
            is_referenced = cmds.referenceQuery(root_joint, inr=True)
            if not is_referenced:
                continue
            ref_path = cmds.referenceQuery(root_joint, filename=True)
            cmds.file(ref_path, importReference=True)

            # update the root joint and get its descendants
            self.logger.info(f"Found root joint {root_joint} for {namespace}")
            root_joint = cmds.parent(root_joint, world=True)[0]

            cmds.select(cl=True)
            new_root_joint = cmds.joint()
            cmds.parent(root_joint, new_root_joint)
            all_joints = cmds.listRelatives(new_root_joint, ad=True, f=True)
            self.objects_to_bake.extend(all_joints)
            self.objects_to_bake.append(new_root_joint)

            # add the geo group and joint root to the list
            self.namespace_to_objects[namespace] = [new_root_joint, scene_asset_inst.geo_grp]

    def add_camera_for_bake(self):
        """
        Find and add the camera for baking
        """
        for namespace in self.namespaces:
            scene_asset_inst = scene_asset.SceneAsset(namespace)
            if not scene_asset_inst.is_camera:
                continue

            # need to set the camera to far focus distance for Unreal
            cam = scene_asset_inst.export_grp
            if not cmds.objExists(f"{cam}.focusDistance"):
                continue

            cmds.setAttr(f"{cam}.focusDistance", 100000)
            self.objects_to_bake.append(cam)
            self.logger.info(f"Camera found for {namespace}")

    def bake_fbx_nodes(self):
        """
        Bake the joints of the rigs for the fbx animation.
        """
        if not self.objects_to_bake:
            self.logger.warning("No joints to bake")
            return
        self.logger.info(f"Baking {len(self.objects_to_bake)} joints: {self.start}-{self.end}")
        cmds.bakeResults(self.objects_to_bake, simulation=True, t=(self.start, self.end))

    def export_fbx_files(self):
        """
        Loop through the namespaces and export each fbx file
        """
        for namespace in self.namespaces:
            self.export_fbx_file(namespace)

    def export_fbx_file(self, namespace):
        # type: (str) -> None
        """
        Export the fbx file from its namespace

        Args:
            namespace: The namespace of the asset to export
        """
        self.logger.info(f"Exporting namespace.... {namespace}")
        objects_to_select = self.namespace_to_objects.get(namespace)
        if not objects_to_select:
            self.logger.info(f"No fbx elements for namespace {namespace}")
            return

        cmds.select(objects_to_select)
        self.logger.info(f"FBX frame range: {self.start}-{self.end} - {namespace}")

        # get export path and directory
        fbx_path = file_utils.join_file_names(self.save_dir, f"{namespace}.fbx")

        # add the fbx path to the dictionary
        self.namespace_to_fbx_path[namespace] = fbx_path
        self.logger.info(f"{namespace}: {fbx_path}")
        self.export_unreal_fbx(fbx_path, self.start, self.end)

    @staticmethod
    def export_unreal_fbx(fbx_path, cache_start, cache_end):
        # type: (str, int, int) -> None
        """
        Export an animated fbx to be compatible with Unreal

        Args:
            fbx_path: Path to export to
            cache_start: Start of the cache
            cache_end: End of the cache
        """
        # select the joint and geometry roots and the hierarchy
        cmds.select(hierarchy=True)

        # run the fbx export commands
        pm.mel.FBXResetExport()
        pm.mel.FBXExportFileVersion(v="FBX201900")
        pm.mel.FBXExportInAscii(v=False)
        pm.mel.FBXExportUpAxis("Y")
        pm.mel.FBXExportScaleFactor(1)
        pm.mel.FBXExportEmbeddedTextures(v=True)
        pm.mel.FBXExportInputConnections(v=True)
        pm.mel.FBXExportIncludeChildren(v=True)
        pm.mel.FBXExportCameras(v=True)
        pm.mel.FBXExportLights(v=True)
        pm.mel.FBXExportConstraints(v=False)
        pm.mel.FBXExportShapes(v=True)
        pm.mel.FBXExportSkins(v=True)
        pm.mel.FBXExportHardEdges(v=False)
        pm.mel.FBXExportSmoothMesh(v=False)
        pm.mel.FBXExportSmoothingGroups(v=True)
        pm.mel.FBXExportBakeComplexAnimation(v=True)
        pm.mel.FBXExportSkeletonDefinitions(v=False)
        pm.mel.FBXExportBakeComplexStart(v=cache_start)
        pm.mel.FBXExportBakeComplexEnd(v=cache_end)
        pm.mel.FBXExportHardEdges(v=False)
        pm.mel.FBXExportTangents(v=True)
        pm.mel.FBXExportAnimationOnly(v=False)
        pm.mel.FBXExportInstances(v=False)

        # set the animation properties
        pm.mel.eval('FBXProperty "Export|IncludeGrp|Animation" -v 1;')
        pm.mel.eval('FBXProperty "Export|IncludeGrp|Animation|Deformation" -v 1;')
        pm.mel.eval('FBXProperty "Export|IncludeGrp|Geometry|SelectionSet" -v 0;')

        # export the fbx path
        pm.mel.FBXExport(f=fbx_path, s=True)
