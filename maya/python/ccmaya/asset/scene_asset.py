import maya.cmds as cmds
import ccmaya.maya_constants as maya_constants


class SceneAsset(object):
    def __init__(self, namespace):
        self.namespace = namespace
        self._geo_grp = str()
        self._cam_grp = str()
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
        for transform in cmds.listRelatives(self.namespace, ad=True, f=True):
            if transform.endswith(find_group):
                return transform

    @property
    def export_grp(self):
        if self.cam_grp:
            return self.cam_grp
        return self.geo_grp

    @property
    def geo_grp(self):
        # type: () -> str
        """
        Get the root node to export the fullpath
        """
        if not self._geo_grp:
            self._geo_grp = self.find_group(maya_constants.GEO_GROUP)
        return self._geo_grp

    @property
    def jnt_grp(self):
        # type: () -> str
        """
        Get the root node to export the fullpath
        """
        if not self._jnt_grp:
            self._jnt_grp = self.find_group(maya_constants.JNT_GROUP)
        return self._jnt_grp

    @property
    def cam_grp(self):
        # type: () -> str
        """
        Get the root node to export the fullpath
        """
        if not self._cam_grp:
            self._cam_grp = self.find_group(maya_constants.CAM_GROUP)
        return self._cam_grp

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