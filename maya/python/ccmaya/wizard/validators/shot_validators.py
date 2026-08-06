""" Maya validators for shot cameras """
import maya.cmds as cmds
from ccgeneral.wizard.validators.base_validators import BaseValidator
import ccmaya.maya_constants as maya_constants


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
        for node in cmds.ls("*.export"):
            asset_name = node.split(".export")[0]
            for node_type, group_name in type_to_prefix.items():

                # check for objects of that type that are descendants
                objects_found = cmds.listRelatives(asset_name, ad=True, type=node_type, f=True)
                if not objects_found:
                    continue
                objects_found.append(asset_name)

                # check there is a group of that name
                found_obj_group = False
                for obj in objects_found:
                    if f"|{group_name}|" in obj:
                        found_obj_group = True

                # add to the list of missing groups
                if not found_obj_group:
                    missing_groups.append(f"{asset_name} is missing {group_name}")

        if missing_groups:
            self.is_valid = False
            missing_groups_str = "\n".join(missing_groups)
            self.message = f"Missing group names:\n{missing_groups_str}"
