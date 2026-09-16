""" Publish the render to ftrack wizard page """
import hou
from CCPySide import QtCore
import cchoudini.utils.hou_utils as hou_utils
import cchoudini.hou_constants as hou_constants
import cchoudini.wizard.widgets.hou_frame_range as hou_frame_range
from ccgeneral.wizard.pages.publish_render_page import PublishRenderRendersPage


# constants
RENDER_NODE_TYPES = hou_constants.RENDER_NODE_TYPES
ROP_TYPE_TO_PICTURE_PARM = hou_constants.ROP_TYPE_TO_PICTURE_PARM
RENDER_NODES_DICT = hou_constants.RENDER_NODES_DICT


class HouPublishRenderRendersPage(PublishRenderRendersPage):
    title = "Publish Renders"
    subtitle = "Publish the Arnold Renders on completion"

    def __init__(self, parent=None):
        super(HouPublishRenderRendersPage, self).__init__(parent)
        self.renderers = list()
        self.rop_path_item_dict = dict()

    def create_layout(self):
        """
        Create the layout of the page
        """
        super().create_layout()

        # add the houdini frame range widget
        self.range_wdg = hou_frame_range.HouFrameRangeWidget()
        self.main_layout.insertWidget(2, self.range_wdg)

    def initializePage(self):
        """
        Add the frame range widget
        """
        super(HouPublishRenderRendersPage, self).initializePage()
        self.confirm_version()
        self.set_frame_range_widget()

    def save_new_file(self, wip_file_path, version_padded):
        # type: (str, str) -> None
        """
        Save the file to the given file path
        """
        hou.hipFile.save(file_name=wip_file_path)
        hou.hscript(f"set -g RENDER_VERSION = {version_padded}")
        self.refresh_image_paths()

    def confirm_version(self):
        """
        Compare the set version to the next ftrack version to
        ensure it is set correctly. If there is a miss match
        then set to the ftrack version
        """
        deadline_node = hou.node(self.data["node_path"])
        rops = hou_utils.input_nodes_of_type(deadline_node, RENDER_NODE_TYPES)

        # find the highest version and set all
        # output paths to the same version
        possible_versions = list()
        for rop in rops:
            picture_parm = ROP_TYPE_TO_PICTURE_PARM[rop.type().name()]
            output_path = rop.parm(picture_parm).eval()
            use_version = self.wizard().ftquery.get_correct_version(output_path)
            possible_versions.append(use_version)

        # get the highest version and set rop paths to that version
        max_version = max(possible_versions)
        version_padded = str(max_version).zfill(3)
        hou.hscript(f"set -g RENDER_VER = {version_padded}")
        hou.hscript(f"set -g VER = {version_padded}")

    def populate_renders(self):
        """
        From the deadline node find all input renders and
        set the path in the tree widget
        """
        self.tw_renders.clear()
        deadline_node = hou.node(self.data["node_path"])
        render_nodes = list(RENDER_NODES_DICT.values())
        rop_nodes = hou_utils.input_nodes_of_type(
            deadline_node,
            render_nodes
        )
        for index, rop in enumerate(rop_nodes):
            node_type_name = rop.type().name()
            picture_parm = ROP_TYPE_TO_PICTURE_PARM[node_type_name]
            renderer = RENDER_NODES_DICT[node_type_name]
            self.renderers.append(renderer)

            output_path = rop.parm(picture_parm).eval()
            start, end = hou_utils.get_frame_range(rop)
            node_range_str = f"{start}-{end}"
            is_renderable = not rop.isBypassed()
            item = self.create_item(is_renderable, rop.name(), output_path, node_range_str, node_type_name, index)
            self.rop_path_item_dict[rop.path()] = item

    def refresh_image_paths(self):
        """
        Refresh the paths in the items so it matches the new version
        """
        for rop_path, item in self.rop_path_item_dict.items():
            rop = hou.node(rop_path)
            node_type_name = rop.type().name()
            picture_parm = ROP_TYPE_TO_PICTURE_PARM[node_type_name]
            output_path = rop.parm(picture_parm).eval()
            item.setData(self.ftrack_movie_index, QtCore.Qt.UserRole, output_path)

    def set_frame_range_widget(self):
        """
        Set the initial frame range on the range widget
        """
        self.range_wdg.ftshot = self.wizard().ftshot
        self.range_wdg.initialize()

    @property
    def use_frame_range(self):
        # type: () -> str
        """ If use node range is selected get the max and min possible range """
        if self.range_wdg.data["range_type"] != hou_frame_range.NODE_RANGE:
            return self.range_wdg.data["frame_range"]

        deadline_node = hou.node(self.data["node_path"])
        render_nodes = list(RENDER_NODES_DICT.values())
        rop_nodes = hou_utils.input_nodes_of_type(
            deadline_node, render_nodes)

        all_ranges = list()
        for rop_node in rop_nodes:
            start, end = hou_utils.get_frame_range(rop_node)
            all_ranges.extend([start, end])
        return f"{min(all_ranges)}-{max(all_ranges)}"

    def validatePage(self):
        # type: () -> bool
        """
        Save the page data

        Returns:
            True if the page is valid
        """
        super().validatePage()
        self.data.update(self.range_wdg.data)
        self.data["frame_range"] = self.use_frame_range
        self.data["renderers"] = self.renderers
        return True

