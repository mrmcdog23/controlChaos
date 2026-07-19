""" Asset validators for Maya """
import maya.cmds as cmds
from ccgeneral.wizard.validators.base_validators import BaseValidator
import ccmaya.utils.maya_utils as maya_utils
import ccmaya.maya_constants as maya_constants


class GeoGroupValidator(BaseValidator):
    """
    Check there is a geo node to publish
    """
    validator_type = 'Does "GEO" node exists'
    task_names = ["rigging", "modeling"]
    ignore_types = ["Camera"]
    is_autofixable = False

    def __init__(self, session, data):
        super(GeoGroupValidator, self).__init__(session, data)

    def validate(self):
        """
        Check that there is a transform called "GEO"
        for the caching and connecting the alembic
        """
        self.is_valid = False
        self.message = f"{maya_constants.GEO_GRP} group that" \
                       f" contains the meshes has not been found"

        # check the geo group exists
        geo_grp = cmds.ls(maya_constants.GEO_GRP)
        if not geo_grp:
            return

        # if meshes are found then the group is valid
        meshes = cmds.listRelatives(geo_grp[0], ad=True, type="mesh")
        if meshes:
            self.is_valid = True
            self.message = "Found the meshes group"


class RigGroupValidator(BaseValidator):
    """
    Check there is a rig node to publish
    """
    validator_type = 'Does "RIG" node exists'
    task_names = ["rigging"]
    ignore_types = ["Camera"]
    is_autofixable = False

    def __init__(self, session, data):
        super(RigGroupValidator, self).__init__(session, data)

    def validate(self):
        """
        Check that there is a transform called "RIG"
        for the caching and connecting the alembic
        """
        self.is_valid = False
        self.message = "Found the rig group"
        top_nodes = maya_utils.get_top_level_nodes()
        for top_node in top_nodes:
            if maya_constants.RIG_GRP == top_node:
                self.is_valid = True
                return
        self.message = "The node containing the rig has not been found"

