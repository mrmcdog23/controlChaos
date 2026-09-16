""" Exporter for fbx publishing """
import sys
import hou
import cccore.file_env.context as context
import cccore.data.server_data as server_data
import ccgeneral.exporter.base_exporter as base_exporter


class FBXExporter(base_exporter.BaseExporter):
    """
    Exporter to create and publish FBX files
    """
    def __init__(self):
        super().__init__()
        self.rop_fbx = None
        self.project_data = server_data.ProjectData()
        self.asset_version_id = None

    def export(self):
        """
        Export the asset and publish it to ftrack
        """
        self.add_progress(20)

        # create asset version on ftrack
        self.create_fbx_asset_version()
        self.export_fbx_nodes()
        self.finish_exporter_process()

    def create_fbx_asset_version(self):
        """
        Create the hda asset version on ftrack for the library
        """
        self.ftasset.category = "Scene"

        self.log("Creating project asset version...")

        # set publish asset data
        self.data["ext"] = "fbx"

        # publish the asset
        self.asset_version = self.ftasset.set_ftrack_data(self.data)
        self.asset_version_id = self.asset_version["id"]
        self.log(f"Asset Version: {self.asset_version_id}")

        self.ftver.asset_version_id = self.asset_version["id"]

    def export_fbx_nodes(self):
        """
        Export the fbx nodes
        """
        number = len(self.data["node_paths"])
        progress = int(80 / number)

        for node_path in self.data["node_paths"]:
            node = hou.node(node_path)
            self.add_fbx_component(node)
            self.add_progress(progress)
        self.rop_fbx.destroy()

    def add_fbx_component(self, node):
        # type: (hou.Node) -> None
        """
        Create a fbx of the asset

        Return:
            fbx_asset_path: Path of the fbx to export
        """
        if not self.rop_fbx:
            self.rop_fbx = node.parent().createNode("rop_fbx")

        node_name = node.name()
        overrides = {
            "ext": "fbx",
            "aov": node_name,
            "version": self.ftver.version_int
        }
        ctx = context.Context(overrides=overrides)
        fbx_asset_path = ctx.next_pub_save_path()

        # set the rop input and render
        self.rop_fbx.setInput(0, node)
        self.rop_fbx.parm("sopoutput").set(fbx_asset_path)
        self.rop_fbx.parm("execute").pressButton()

        # add the fbx component
        self.ftver.add_component_dict({node_name: fbx_asset_path})
        self.log(f"Export FBX path: {fbx_asset_path}")


if __name__ == "__main__":
    exporter = FBXExporter()
    exporter.batch_process(sys.argv[1])

