""" USD Render rop node setup """
from typing import Optional
import cccore.utils.cc_logging as cc_logging
import cccore.file_env.context as context


# extension mappings
EXT_MAPPINGS = {
    "driver_deepexr": "exr",
    "driver_exr": "exr",
    "driver_jpeg": "jpeg",
    "driver_png": "png",
    "driver_tiff": "tif"
}


class USDRenderRopNode(object):
    """
    Set up the render rop and functions
    """
    def __init__(self, usdrender_rop_node=None, render_settings_node=None):
        # type: (Optional[hou.Node], Optional[hou.Node]) -> None
        """
        Args:
            usdrender_rop_node: The usd render node to manager
            render_settings_node: The render settings node
        """
        self.usdrender_rop_node = usdrender_rop_node
        self.render_settings_node = render_settings_node or self.find_render_settings_node
        self.logger = cc_logging.cc_logger()

    @property
    def find_render_settings_node(self):
        # type: () -> hou.Node
        """
        From the USD render node get the arnold settings node
        """
        for input_node in self.usdrender_rop_node.inputAncestors():
            if input_node.type().name() == "arnold_rendersettings":
                return input_node

    def set_render_settings_node_path(self, use_version=None):
        # type: (Optional[int]) -> None
        """
        Set the path of the render settings node
        """
        arnold_driver = self.render_settings_node.parm("xn__arnolddriver_mva").evalAsString()
        ext = EXT_MAPPINGS[arnold_driver]
        overrides = {"aov": self.render_settings_node.name(),
                     "ext": ext
                     }
        if use_version:
            overrides["version_num"] = use_version

        # set the output path
        ctx = context.Context(overrides=overrides)
        ctx.use_next_sequence_version()
        self.render_settings_node.parm("productName").set(ctx.hou_sequence_path)

    @property
    def output_path(self):
        # type: () -> str
        """
        The render settings output path
        """
        return self.render_settings_node.parm("productName").evalAsString()
