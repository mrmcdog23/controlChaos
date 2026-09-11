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
    validator_type = 'Are rig group names correct'
    task_names = ["rigging"]
    ignore_types = ["Camera"]
    is_autofixable = False

    def __init__(self, session, data):
        super(RigGroupValidator, self).__init__(session, data)

    def check_hierarchy_for_names(self, object_type, group_name):
        # type: (str, str) -> str
        """
        Check the rigs hierarchy for the correct group names

        Args:
            object_type: The object type to check for
            group_name: The group name to check for
        """
        all_objects = cmds.listRelatives(maya_constants.RIG_GRP, type=object_type, ad=True, f=True)
        if not all_objects:
            return
        for node in all_objects:
            if group_name in node:
                return
        return f"Group named '{group_name}' group not found for {object_type}"

    def validate(self):
        """
        Check that there is a transform called "RIG"
        for the caching and connecting the alembic
        """
        # check for rig group
        rig_group_found = False
        top_nodes = maya_utils.get_top_level_nodes()
        for top_node in top_nodes:
            if maya_constants.RIG_GRP == top_node:
                rig_group_found = True
                break

        if not rig_group_found:
            self.message = f"Group named '{maya_constants.RIG_GRP}' group not found"
            self.is_valid = False
            return

        object_type_to_group = {
            "joint": maya_constants.JNT_GRP,
            "mesh": maya_constants.GEO_GRP,
            "nurbsCurve": maya_constants.CTLS_GRP
        }

        # go through all the objects types to check their groups exist
        self.message = str()
        for object_type, group_name in object_type_to_group.items():
            message = self.check_hierarchy_for_names(object_type, group_name)
            if message:
                self.message += message + "\n"

        if self.message:
            self.is_valid = False
        else:
            self.is_valid = True
            self.message = "Found the rig group"


class OnlyOneTopLevelNodeValidator(BaseValidator):
    """
    Check there is only one top level group
    """
    validator_type = 'Is there only one top level node'
    is_autofixable = False

    def __init__(self, session, data):
        super(OnlyOneTopLevelNodeValidator, self).__init__(session, data)

    def validate(self):
        """
        Check that there is a transform called "RIG"
        for the caching and connecting the alembic
        """
        top_nodes = maya_utils.get_top_level_nodes()
        if len(top_nodes) == 1:
            self.message = "Only one top node found"
            self.is_valid = True
        else:
            self.message = "More than one top level node in the outliner"
            self.is_valid = False

