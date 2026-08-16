import maya.cmds as cmds
import ccmaya.maya_constants as maya_constants


class SceneAsset(object):
    def __init__(self, namespace):
        self.namespace = namespace
        self._geo_grp = str()
        self._cam_grp = str()
        self._env_grp = str()
        self._jnt_grp = str()

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
    def export_grp(self):
        if self.is_camera:
            return self.namespace
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
        """
        Get the root node to export the fullpath
        """
        if not self._jnt_grp:
            self._jnt_grp = self.find_group(maya_constants.JNT_GRP)
        return self._jnt_grp

    @property
    def cam_grp(self):
        # type: () -> str
        """
        Get the root node to export the fullpath
        """
        camera_tran = cmds.ls(self.namespace, type="transform")
        if not camera_tran:
            return
        camera_shape = cmds.listRelatives(camera_tran[0], type="camera")
        if not camera_shape:
            return
        return camera_shape[0]

    @property
    def root_joint(self):
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
            abc_args = " ".join(maya_constants.CAM_ABC_ARGS)
        else:
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
