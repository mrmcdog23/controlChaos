""" Maya validators for shot cameras """
import maya.cmds as cmds
from ccgeneral.wizard.validators.base_validators import BaseValidator
import ccmaya.maya_constants as maya_constants
import ccmaya.utils.maya_utils as maya_utils


class GroupsNamedCorrectlyValidator(BaseValidator):
    """
    Validate all groups are the right name
    """
    validator_type = 'Groups named correctly'

    def __init__(self, data):
        super().__init__(data)

    def validate(self):
        """
        Check all group names are correct
        """
        self.is_valid = True
        self.message = "All groups are named correctly"

        type_to_prefix = {
            "mesh":  maya_constants.GEO_GRP,
            "camera": maya_constants.CAM_GRP,
            "joint": maya_constants.JNT_GRP
            }
        missing_groups = list()

        for asset_name in maya_utils.get_shot_assets():
            objects_found = cmds.ls(f"{asset_name}:*", type="transform")
            if not objects_found:
                continue

            # check there is a group of that name
            found_obj_group = False
            for node_type, group_name in type_to_prefix.items():
                for obj in objects_found:
                    if obj.endswith(group_name):
                        found_obj_group = True
                        break

            # add to the list of missing groups
            if not found_obj_group:
                missing_groups.append(f"{asset_name} is missing {group_name}")

        if missing_groups:
            self.is_valid = False
            missing_groups_str = "\n".join(missing_groups)
            self.message = f"Missing group names:\n{missing_groups_str}"
