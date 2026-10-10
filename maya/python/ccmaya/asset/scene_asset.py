import maya.cmds as cmds
import ccmaya.maya_constants as maya_constants
import cccore.utils.cc_logging as cc_logging
import ccftrack.asset_version as asset_version


class SceneAsset(object):
    def __init__(self, namespace=None, session=None, ref_node=None):
        self.namespace = namespace
        self._geo_grp = str()
        self._cam_grp = str()
        self._env_grp = str()
        self._jnt_grp = str()
        self._ref_node = ref_node
        self.logger = cc_logging.cc_logger()
        self.ftver = asset_version.FtAssetVersion(session=session)
        self.set_asset_version()

    @property
    def reference_node(self):
        # type: () -> str
        """ The asset reference node """
        if not self._ref_node:
            use_object = self.find_ftrack_id_attributes(self.namespace)
            if not use_object:
                use_object = cmds.ls(f"{self.namespace}:*")[0]
            self._ref_node = cmds.referenceQuery(use_object, referenceNode=True)
        return self._ref_node

    @property
    def is_camera(self):
        return bool(self.cam_grp)

    def find_group(self, find_group):
        # type: () -> str
        """
        Get the root node to export the fullpath
        """
        if self.namespace == find_group:
            return self.namespace
        transform = cmds.ls(f"{self.namespace}:{find_group}", type="transform")
        if transform:
            return transform[0]

    @property
    def is_skeleton_mesh(self):
        # type: () -> bool
        """ Is a static mesh """
        return bool(self.jnt_grp)

    @property
    def export_grp(self):
        if self.is_camera:
            return self.cam_grp
        if self.geo_grp:
            return self.geo_grp

    @property
    def geo_grp(self):
        # type: () -> str
        """ Get the root node to export the fullpath """
        if not self._geo_grp:
            self._geo_grp = self.find_group(maya_constants.GEO_GRP)
        return self._geo_grp

    @property
    def env_grp(self):
        # type: () -> str
        """ Get the root node to export the fullpath """
        if not self._env_grp:
            self._env_grp = self.find_group(maya_constants.ENV_GRP)
        return self._env_grp

    @property
    def jnt_grp(self):
        # type: () -> str
        """ Get the root node to export the fullpath """
        if not self._jnt_grp:
            self._jnt_grp = self.find_group(maya_constants.JNT_GRP)
        return self._jnt_grp

    @property
    def cam_grp(self):
        # type: () -> str
        """ Get the root node to export the fullpath """
        camera_tran = cmds.ls(f"{self.namespace}:CAM", type="transform")
        if not camera_tran:
            return
        return camera_tran[0]

    @property
    def root_joint(self):
        # type: () -> str
        """ Get the root joint to export the fullpath """
        joints = cmds.listRelatives(self.jnt_grp, type="joint", f=True)
        if not joints:
            return
        return joints[0]

    @property
    def abc_export_args(self):
        # type: () -> str
        """
        Alembic export args. These vary on the object type to cache

        Returns:
            abc_args: String list of AbcExport arguments
        """
        if self.is_camera:
            self.logger.info("Is a camera asset")
            abc_args = " ".join(maya_constants.CAM_ABC_ARGS)
        else:
            self.logger.info("Is not a camera asset")
            abc_args = " ".join(maya_constants.MESH_ABC_ARGS)
        return abc_args

    @property
    def cam(self):
        if not self.cam_grp:
            return
        cameras = cmds.listRelatives(self.cam_grp, type="transform", f=True)
        if cameras:
            return cameras[0]

    @property
    def reference_node(self):
        # type: () -> Optional[str]
        """ From a namespace get the reference node """
        for ref_node in cmds.ls(type="reference"):
            try:
                node_namespace = cmds.referenceQuery(ref_node, namespace=True)
                if node_namespace.endswith(self.namespace):
                    return ref_node
            except RuntimeError:
                pass

    @property
    def reference_path(self):
        # type: () -> str
        """ Path of the referenced file """
        if self.reference_node:
            reference_path = cmds.referenceQuery(self.reference_node, filename=True)
        else:
            objects = cmds.ls(f"{self.namespace}:*")
            if not objects:
                return
            reference_path = cmds.referenceQuery(objects[0], filename=True)
        self._ref_path = reference_path.split("{")[0]
        return self._ref_path

    @property
    def ftrack_id(self):
        # type: () -> str
        """ The ftrack asset id """
        ftrack_ids = cmds.ls(f"{self.namespace}:*.ftrackId")
        if not ftrack_ids:
            return
        return cmds.getAttr(ftrack_ids[0])

    @property
    def node(self):
        ftrack_attr = cmds.ls(f"{self.namespace}:*.ftrackId")
        if ftrack_attr:
            return ftrack_attr[0].split(".")[0]

    @property
    def asset_data_dict(self):
        # type: () -> dict
        """ The asset dictionary """
        file_data = {
            "is_camera": self.is_camera,
            "is_skeleton_mesh": self.is_skeleton_mesh,
            "namespace": self.namespace,
            "reference_path": self.reference_path,
            "asset_fbx_path": self.asset_fbx_path,
            "ftrack_id": self.ftrack_id
        }
        return file_data

    @property
    def asset_top_node(self):
        # type: () -> str
        """
        Get the top node of the asset group
        """
        parent_node = cmds.listRelatives(self.export_grp, p=True)
        if not parent_node:
            return self.export_grp
        if self.namespace not in parent_node:
            return parent_node

    def set_asset_version(self):
        """
        Set the asset version id from the asset in the scene
        """
        if self.ftrack_id:
            self.ftver.asset_version_id = self.ftrack_id
        else:
            av = self.ftver.asset_version_from_path(self.reference_path)
            self.ftver.asset_version_id = av["id"]
            self._asset_version = av

    @property
    def is_loaded(self):
        # type: () -> bool
        """ Is the reference loaded """
        return cmds.referenceQuery(self.reference_node, isLoaded=True)

    def toggle_load(self):
        """ Toggle the reference load state """
        if self.is_loaded:
            cmds.file(self.reference_path, unloadReference=self.reference_node)
        else:
            cmds.file(self.reference_path, loadReference=self.reference_node)

    def update_to_version(self, new_version):
        # type: (Any) -> None
        """
        Update the asset to a new version

        Args:
            new_version: Version to update to
        """
        self.ftver.asset_version_id = new_version['id']
        ref_path = self.ftver.master_component_path
        cmds.file(ref_path, loadReference=self.reference_node)

    def remove_reference(self):
        """
        Remove the asset from the scene. Remove foster
        node that gets created after removal
        """
        prev_foster_nodes = cmds.ls(self.namespace + "*", type="fosterParent")
        cmds.file(removeReference=True, referenceNode=self.reference_node, type='mayaAscii')
        for foster_node in cmds.ls(self.namespace + "*", type="fosterParent"):
            if foster_node not in prev_foster_nodes:
                cmds.delete(foster_node)
        if self.alembic_path:
            cmds.file(self.alembic_path, removeReference=True)

    @property
    def asset_fbx_path(self):
        # type: () -> str
        """ Path of the fbx component """
        return self.ftver.fbx_component_path
