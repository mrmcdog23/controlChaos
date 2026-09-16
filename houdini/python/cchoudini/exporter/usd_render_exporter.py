""" Run USD render on the given node """
import sys
import hou
import ccgeneral.exporter.base_exporter as base_exporter
import cchoudini.utils.hou_utils as hou_utils
import cchoudini.node.usdrender_rop_node as usdrender_rop_node


class USDRenderExporter(base_exporter.BaseExporter):
    def __init__(self):
        super().__init__()
        self.start = int()
        self.end = int()
        self.total = int()

    def open_file(self):
        """
        Load the hip file
        """
        wip_file_path = self.data["wip_file_path"]
        self.logger.info(f"Opening {wip_file_path}")
        hou.hipFile.load(wip_file_path,
                         suppress_save_prompt=True,
                         ignore_load_warnings=True
                         )

    def export(self):
        """
        Loop through the connected arnold ROPs
        and generate the ass files
        """
        usd_submit_node = hou.node(self.data["node_path"])
        self.logger.info(f"Caching {usd_submit_node} frame range: {self.start}-{self.end}")
        hou_utils.set_rop_frame_range(usd_submit_node, self.start, self.end)
        usd_submit_node.parm("execute").pressButton()
        usd_inst = usdrender_rop_node.USDRenderRopNode(usd_submit_node)
        self.logger.info(f"Rendered path: {usd_inst.output_path}")
        self.logger.info("Complete")


if __name__ == "__main__":
    exporter = USDRenderExporter()
    metadata_file = sys.argv[1]
    exporter.start = int(sys.argv[2])
    exporter.end = int(sys.argv[3])
    try:
        exporter.tile_number = int(sys.argv[5])
    except IndexError:
        pass
    exporter.batch_process(metadata_file)
