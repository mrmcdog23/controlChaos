""" Houdini comp rop exporter """
import hou
import sys
import os
import ccgeneral.exporter.base_exporter as base_exporter
import cccore.utils.sequence_utils as sequence_utils
import cccore.utils.file_utils as file_utils
import cchoudini.utils.hou_utils as hou_utils


class CompExporter(base_exporter.BaseExporter):
    def __init__(self):
        super(CompExporter, self).__init__()

    def open_file(self):
        """
        Load the hip file
        """
        hou.hipFile.load(self.data["wip_file_path"],
                         suppress_save_prompt=True
                         )

    def export(self):
        """
        Loop through the connected arnold ROPs
        and generate the ass files
        """
        deadline_node = hou.node(self.data["node_path"])
        comp_rop = hou_utils.input_nodes_of_type(deadline_node, ["comp"])[0]
        self.logger.info(f"Comp ROP...{comp_rop}")

        # render the ass files
        comp_path = comp_rop.parm("copoutput").eval()
        file_utils.create_directories(os.path.dirname(comp_path))

        # generate comp sequence
        comp_sequence = sequence_utils.convert_frame_to_sequence(comp_path)
        self.logger.info(f"Generating comp sequence...{comp_sequence}")

        # set new frame range
        hou_utils.set_rop_frame_range(comp_rop, self.data["start"], self.data["end"])
        comp_rop.parm("execute").pressButton()

        self.logger.info("Complete")


if __name__ == "__main__":
    exporter = CompExporter()
    exporter.batch_process(sys.argv[1])
