""" Asset loader for houdini """
import hou
import cccore.utils.sequence_utils as sequence_utils
import ccgeneral.asset.asset_loader as asset_loader
import cchoudini.node.ftrack_hou_node as ftrack_hou_node
import cchoudini.asset.load_published_alembic as load_published_alembic
import cchoudini.utils.node_utils as node_utils
import cchoudini.utils.hou_utils as hou_utils
import ccftrack.query as query


class HouAssetLoader(asset_loader.AssetLoaderBase):
    title = "Houdini Load Asset"
    SUPPORTED_EXT = ["bgeo.sc", "hda", "usd", "abc"]

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._geo_node = None
        self.ftquery = query.FtQuery(session=self.ftver.session)
        self.stay_on_top()
        self.set_widget_font_size(self.title_asset, 25)
        self.set_widget_font_size(self.title_loader, 25)

    @property
    def geo_node(self):
        # type: () -> hou.Node
        """ The geo node under the obj context """
        if not self._geo_node:
            self._geo_node = hou.node("/obj").createNode("geo", self.asset_name)
        return self._geo_node

    def load_hda(self, component_name, component_path):
        # type: (str, str) -> None
        """
        Create the hda file node

        Args:
            component_name: Name of the component to load
            component_path: Path of the hda to load
        """
        metadata = self.ftver.av_metadata
        category = metadata["category"]
        parent_node = None
        if category == "Sop":
            parent_node = self.geo_node

        elif category == "Object":
            parent_node = hou.node("obj")

        # load the hda through the class
        node_utils.load_published_hda(parent_node, self.ftver, component_name, component_path)

    def load_cache_sequence(self, cache_sequence_path):
        # type: (str) -> None
        """
        Create the cache file node and set the houdini sequence

        Args:
            cache_sequence_path: Path of th cache sequence
        """
        seq_data = sequence_utils.get_sequence_data(cache_sequence_path)
        geo_name = f"{self.asset_name}_cache"
        file_node = self.geo_node.createNode("file", geo_name)
        if seq_data.is_single_frame:
            file_node.parm("file").set(seq_data.first_frame)
        else:
            file_node.parm("file").set(seq_data.houdini_path)
        file_node.moveToGoodPosition()

    def load_selected_version(self):
        """
        Load the selected asset version
        """
        self.save_ui_settings(self.ui_settings)

        # list components in the asset version
        self.asset_name = self.ftver.asset_build_name
        ext_tuple = tuple(self.SUPPORTED_EXT)
        component_paths = self.ftver.get_component_path_dict(ext_tuple)
        path_component = dict(zip(component_paths.values(), component_paths.keys()))

        for component_path in self.selected_components:

            component_name = path_component[component_path]
            if component_path.endswith("hda"):
                self.load_hda(component_name, component_path)
                return

            elif component_path.endswith(("bgeo.sc", "vdb")):
                self.load_cache_sequence(component_path)
                return

        if self.ftver.cache_path:
            abc_load_inst = load_published_alembic.LoadPublishedAlembic(
                self.ftver.cache_path,
                self.ftver.materialx_component_path,
                self.ftver.metadata_component_path,
                self.asset_name
            )

            # add the ftrack parameters
            component_name = "Alembic"
            ftnode = ftrack_hou_node.FTrackHouNode(abc_load_inst.geo_node, self.ftver, component_name)
            ftnode.add_ftrack_parameters()


def main():
    """
    Launch the loader
    """
    hou.hscript("otrefresh -r")
    hou_utils.launch_hou_win(HouAssetLoader)
