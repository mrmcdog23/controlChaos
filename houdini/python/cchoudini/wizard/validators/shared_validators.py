""" Validators to be used either on assets or shots """
import hou
import cchoudini.hou_constants as hou_constants
import cchoudini.utils.hou_utils as hou_utils
from ccgeneral.wizard.validators.base_validators import BaseValidator, BasePathCorrectForProject


class RenderCameraFoundValidator(BaseValidator):
    """
    Run check for a valid render camera
    """
    validator_type = "Is the render camera valid on the rops"
    is_autofixable = False
    node_types = ["ccsubmit"]

    def __init__(self, session, data):
        super().__init__(session, data)
        self.camera_nodes = list()

    def validate(self):
        """
        Check there is a valid render camera in the scene
        """
        self.message = str()
        for submitter in hou_utils.get_rop_type(hou_constants.SUBMITTER):
            arnold_rops = hou_utils.input_nodes_of_type(submitter, ["arnold"])
            for arnold_rop in arnold_rops:
                rop_name = arnold_rop.name()
                camera_path = arnold_rop.parm("camera").evalAsString()
                camera_node = hou.node(camera_path)

                # if there is no camera node then it doesn't exist
                if not camera_node:
                    self.message += f"{camera_path} camera doesn't exist on {rop_name}\n"
                    self.is_valid = False
                    continue

                # if the camera is None then it is not set
                if camera_node is None:
                    self.message += f"Camera is not set {rop_name}\n"
                    self.is_valid = False
                    continue

                # if the object type is not a camera then give warning
                object_type = camera_node.type().name()
                if object_type != "cam":
                    self.message += f"{camera_path} is not a camera on {rop_name}\n"
                    self.is_valid = False

        if not self.message:
            self.is_valid = True
            self.message = "All cameras are valid"


class IsFilePathCorrectForProject(BasePathCorrectForProject):
    """
    Is the file path correct for the project
    """
    def __init__(self, session, data):
        super().__init__(session, data)
        self.file_path = hou.hipFile.path()


class TexturePathsLocal(BaseValidator):
    """
    Check any nodes with local texture paths
    """
    validator_type = "Are any texture paths local"
    is_autofixable = False
    node_types = ["ccsubmit"]

    def __init__(self, session, data):
        super().__init__(session, data)
        self.local_texture_nodes = list()

    def validate(self):
        """
        Check there is are any local textures
        """
        self.local_texture_nodes = list()

        obj_node = hou.node("/obj")
        arnold_light_nodes = hou_utils.find_all_subnodes_of_types(
            obj_node, ["arnold_light", "alembic", "alembicxform"])
        for arnold_light_node in arnold_light_nodes:

            # if the parameter does not exist
            for parm_name in ["ar_light_color_texture", "fileName"]:
                parm = arnold_light_node.parm(parm_name)
                if parm:
                    break
            if not parm:
                continue
            texture_path = parm.eval()
            if texture_path.startswith("/home/"):
                node_path = arnold_light_node.path()
                self.local_texture_nodes.append(node_path)

        # pass if no nodes found
        if self.local_texture_nodes:
            self.is_valid = False
            local_nodes = "\n".join(self.local_texture_nodes)
            self.message = f"Nodes with local paths:\n\n{local_nodes}"
        else:
            self.is_valid = True
            self.message = "Node nodes with local paths found"
