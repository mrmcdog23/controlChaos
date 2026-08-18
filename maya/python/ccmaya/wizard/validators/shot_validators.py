""" Maya validators for shot cameras """
import maya.cmds as cmds
from ccgeneral.wizard.validators.base_validators import BaseValidator
import ccmaya.maya_constants as maya_constants
import ccmaya.utils.maya_utils as maya_utils
import ccmaya.asset.scene_asset as scene_asset


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

        for asset_name in maya_utils.get_shot_namespaces():
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



class AreGroupsAtDefaultValuesValidator(BaseValidator):
    """
    Validate all groups are at default values
    """
    validator_type = 'Are Groups at default values'

    def __init__(self, data):
        super().__init__(data)
        self.is_valid = True
        self.message = "All rigs at default"

    def is_transform_default(self, node, tolerance=1e-6):
        """
        Check if a transform node is at its default TRS values.
        """
        defaults = {
            'translate': (0.0, 0.0, 0.0),
            'rotate': (0.0, 0.0, 0.0),
            'scale': (1.0, 1.0, 1.0),
        }

        for attr, default_vals in defaults.items():
            current_vals = cmds.getAttr(f'{node}.{attr}')[0]  # returns list of one tuple
            for current, default in zip(current_vals, default_vals):
                if abs(current - default) > tolerance:
                    return False
        return True

    def get_all_joints_assets_transforms(self):
        """
        Get all groups transforms
        """
        namespace_to_transforms = dict()
        for namespace in maya_utils.get_shot_namespaces():
            scene_asset_inst = scene_asset.SceneAsset(namespace)

            # if it's not a joint group skip
            if not scene_asset_inst.jnt_grp:
                continue

            trans = scene_asset_inst.jnt_grp
            count = 1
            all_transforms = list()
            while trans:
                # keep checking the parent nodes
                trans = cmds.listRelatives(trans, type="transform", p=True)
                if trans:
                    all_transforms.extend(trans)

                # add in a break to avoid the while loop
                count += 1
                if count == 10:
                    break

            # store the parent nodes in the validator
            namespace_to_transforms[namespace] = all_transforms
        return namespace_to_transforms

    def validate(self):
        """
        Check all group names are correct
        """
        groups_not_at_default = str()
        namespace_to_transforms = self.get_all_joints_assets_transforms()
        for namespace, all_transforms in  namespace_to_transforms.items():

            # check the transforms are at default
            not_default = list()
            for transform in all_transforms:
                is_default = self.is_transform_default(transform)
                if not is_default:
                    not_default.append(transform)

            # if not default add to the list
            if not_default:
                not_default_str = ",".join(not_default)
                groups_not_at_default += f"{namespace}: {not_default_str}\n"

        if groups_not_at_default:
            self.is_valid = False
            self.message = groups_not_at_default