""" Houdini ingest loader """
import hou
from CCPySide import QtWidgets
from cchoudini.shot.build_scene import BuildHoudiniScene
from ccgeneral.shot.ingest_loader.ingested_loader import BaseIngestLoader
import cchoudini.utils.hou_utils as hou_utils
import cchoudini.panel.create_cc_panel as create_cc_panel
import cccore.file_env.context as context


class IngestLoader(BaseIngestLoader):
    """
    The houdini shot loader to bring in published assets
    """
    SUPPORTED_EXT = ["cpio", "abc", "exr", "fbx", "jpeg", "bgeo.sc", "vdb"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_nodes = list()
        self.chk_load_hda = None
        self.add_hda_checkbox()

    def add_hda_checkbox(self):
        """
        Create checkbox whether to load as an hda or node
        """
        self.chk_load_hda = QtWidgets.QCheckBox("Load HDA Over Assets")
        self.chk_load_hda.setChecked(True)
        self.lyt_options.addWidget(self.chk_load_hda)

    @property
    def shot_assets(self):
        # type: () -> dict
        """
        Get the scenes current assets
        """
        return hou_utils.get_shot_assets(session=self.ftshot.session)

    def set_context_panel(self):
        """
        Set the context panel buttons and environment
        """
        ctx_panel = create_cc_panel.get_ctx_panel()
        overrides = self.cmb_shot.get_data()
        ctx = context.Context(overrides=overrides)
        ctx.use_task = "animation"
        ctx_panel.set_buttons_from_ctx(ctx)

    def load_shot(self):
        """
        Get the checked data and build the assets
        """
        self.set_context_panel()
        self.build_ingested_scene()
        self.create_group_box()
        self.set_shot_frame_range()
        self.set_scene_image_plane()

    def build_ingested_scene(self):
        """
        From the import data build the scene
        """
        import_data = self.get_import_data()

        xpos = 0
        ypos = 0
        count = 0
        load_hda = self.chk_load_hda.isChecked()
        for asset_version_id, component_to_path in import_data.items():
            self.ftver.asset_version_id = asset_version_id
            build_scene_inst = BuildHoudiniScene(
                asset_version_id,
                self.ftver.session,
                component_to_path=component_to_path,
                xpos=xpos,
                ypos=ypos,
                count=count,
                load_hda=load_hda
            )
            build_scene_inst.create_scene()

            # calculate the gaps between the groups
            xpos = build_scene_inst.xpos
            ypos = build_scene_inst.ypos
            count = build_scene_inst.count
            self.all_nodes.extend(build_scene_inst.shot_nodes)

    def set_shot_frame_range(self):
        """
        Set the shot frame range
        """
        if self.ftshot.is_longform:
            self.ftshot.episode_name = self.cmb_shot.episode_name
        self.ftshot.sequence_name = self.cmb_shot.sequence_name
        self.ftshot.shot_name = self.cmb_shot.shot_name
        hou.playbar.setFrameRange(self.ftshot.start, self.ftshot.end)

    def set_scene_image_plane(self):
        """
        Set the image sequence on the camera
        """
        plate_seq_data = self.plate_seq_data
        if not plate_seq_data:
            return
        for node in self.all_nodes:
            if node.type().name() == "alembicarchive":
                camera_node = hou_utils.find_subnode_of_type(node, "cam")
                camera_node.parm("vm_background").set(plate_seq_data.houdini_path)

    def create_group_box(self):
        """
        Create a network box around the imported nodes
        """
        if not self.all_nodes:
            return
        sequence_name = self.cmb_shot.sequence_name
        shot_name = self.cmb_shot.shot_name
        title = f"{sequence_name}_{shot_name}"
        if self.cmb_shot.episode_name:
            title = f"{self.cmb_shot.episode_name}_{title}"
        hou_utils.create_network_box(
            self.all_nodes, title, colour=hou.Color(0.5, 0.0, 0.7)
        )


def launch():
    """
    Launch the loader
    """
    hou_utils.launch_hou_win(IngestLoader)
