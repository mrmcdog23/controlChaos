""" Shot specific validators """
import os
import hou
import cccore.file_env.context_utils as context_utils
import cccore.core_constants as core_constants
import cchoudini.node.usdrender_rop_node as usdrender_rop_node
import cchoudini.utils.hou_utils as hou_utils
from ccgeneral.wizard.validators.base_validators import BaseValidator, \
    BaseFtrackRangeValidator


class InvalidCacheNodesValidator(BaseValidator):
    """
    Ensure all cache nodes have valid paths
    """
    validator_type = "Are cache paths valid"
    is_autofixable = False
    node_types = ["ignore_for_now"]

    def __init__(self, session, data):
        super().__init__(session, data)
        self.invalid_nodes = list()

    def validate(self):
        """
        Check the current shot frame range is the same as Ftrack
        """
        self.is_valid = False
        self.invalid_nodes = list()
        nodes = hou.node("/").allSubChildren()
        for node in nodes:
            node_type = node.type().name()
            if node_type != "filecache::2.0":
                continue
            filepath = node.parm("sopoutput").evalAsString()
            if not os.path.exists(filepath):
                self.invalid_nodes.append(node.path())

        if self.invalid_nodes:
            invalid_paths_str = "\n".join(self.invalid_nodes)
            self.message = f"Nodes with invalid cache paths: {invalid_paths_str}"
            self.is_valid = False
        else:
            self.message = "All cache nodes are good"
            self.is_valid = True


class FtrackRangeValidator(BaseFtrackRangeValidator):
    """
    Run check the frame range on ftrack matches
    """
    node_types = ["ccsubmit", "cccache"]

    def __init__(self, session, data):
        super().__init__(session, data)

    def scene_frame_range(self):
        # type: () -> (int, int)
        """
        Get the frame range of the houdini file

        Returns:
            Start and end frame of the play bar
        """
        current_start, current_end = hou.playbar.frameRange()
        return int(current_start), int(current_end)


class USDOutputPathValidator(BaseValidator):
    """
    Run check the frame range on ftrack matches
    """
    is_autofixable = True
    validator_type = "Is the output path valid"
    node_types = ["usdrender_rop"]

    def __init__(self, session, data):
        super().__init__(session, data)
        rop_node = hou.node(self.data["node_path"])
        self.usd_inst = usdrender_rop_node.USDRenderRopNode(rop_node)

    def validate(self):
        """
        Check the output path is valid and the version is good
        """
        self.message = "Version number is correct"
        self.is_valid = True

        render_settings_node = self.usd_inst.render_settings_node
        output_path = render_settings_node.parm("productName").eval()
        ctx = context_utils.get_context_from_path(output_path)
        if not ctx:
            self.message = f"Path is invalid: {output_path}"
            self.is_valid = False
            return

        use_version = self.ftquery.get_correct_version(output_path)
        if int(ctx.version) != int(use_version):
            self.message = f"Version in correct. Its currently {ctx.version} " \
                           f"but the next is {use_version}"
            self.is_valid = False
        else:
            self.message = "Version number is correct"
            self.is_valid = True

    def fix(self):
        """
        Run fix output path
        """
        self.usd_inst.set_render_settings_node_path()
        use_version = self.ftquery.get_correct_version(self.usd_inst.output_path)
        self.usd_inst.set_render_settings_node_path(use_version=use_version)


class ReferencePathsValidator(BaseValidator):
    """
    Check nodes have paths that exists and are
    on the network or they will fail on the farm
    """
    validator_type = "Do nodes paths on the network and exists"
    NODE_TYPES = ["alembic", "kinefx::fbxcharacterimport"]
    SEQUENCE_EXT_TUPLE = tuple(core_constants.SEQUENCE_TYPES)

    def __init__(self, session, data):
        super().__init__(session, data)

    def validate(self):
        """
        Check the nodes paths exist and are valid
        """
        self.message = "All node paths are network based"
        self.is_valid = True

        # find all nodes and check their parameters
        invalid_nodes_set = set()
        ref_nodes = hou_utils.find_all_subnodes_of_types(hou.node("/"), self.NODE_TYPES)
        for ref_node in ref_nodes:
            for parm in ref_node.allParms():
                value = parm.evalAsString()
                if value == "default.abc":
                    continue

                # if the path is local then it is invalid
                if value.startswith("/home/"):
                    invalid_nodes_set.add(ref_node.path())

                elif value.endswith(self.SEQUENCE_EXT_TUPLE) and not os.path.exists(value):
                    invalid_nodes_set.add(ref_node.path())

        if invalid_nodes_set:
            invalid_nodes_text = "\n".join(invalid_nodes_set)
            self.message = f"Nodes with local paths:\n{invalid_nodes_text}"
            self.is_valid = False

'''
class IsFileVersionPublished(BaseValidator):
    """
    If the current file version published
    """
    is_autofixable = False
    validator_type = "Is the current file version published"
    node_types = ["ccsubmit"]

    def __init__(self, session, data):
        super().__init__(session, data)
        self.ctx = None
        self.publish_version_num = list()

    def validate(self):
        """
        Check the output path is valid and the version is good
        """
        # get the current version and published versions
        current_path = hou.hipFile.path()
        self.ctx = context_utils.get_context_from_path(current_path)
        self.publish_version_num = self.ftquery.published_version_numbers_from_ctx(self.ctx)

        if self.publish_version_num and self.ctx.version_int in self.publish_version_num:
            self.message = "Version number is already published"
            self.is_valid = False
        else:
            self.message = "Version number is not published"
            self.is_valid = True

'''