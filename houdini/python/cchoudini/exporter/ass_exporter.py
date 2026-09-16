"""
Create asset files from arnold ROP
"""
import hou
import sys
import os
import ccgeneral.exporter.base_exporter as base_exporter
import cccore.utils.sequence_utils as sequence_utils
import cccore.utils.file_utils as file_utils
import cchoudini.utils.hou_utils as hou_utils


class AssExporter(base_exporter.BaseExporter):
    def __init__(self):
        super(AssExporter, self).__init__()
        self.start = int()
        self.end = int()
        self.total = int()
        self.created = 0

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

    def ass_file_progress(self, rop_node, render_event_type, time):
        # type: (hou.Node, hou.ropRenderEventType, float) -> None
        """
        The progress of the ass file generation

        Args:
            rop_node: The arnold rop node
            render_event_type: Callback type
            time: The time taken
        """
        if render_event_type == hou.ropRenderEventType.PostFrame:
            self.created += 1
            if self.total == 0:
                return
            self.logger.info(f"Created: {self.created}   total: {self.total}")
            progress_decimal = float(self.created) / float(self.total)
            progress = int(progress_decimal * 100)
            self.logger.info(f"Progress: {progress}%")

    def export(self):
        """
        Loop through the connected arnold ROPs
        and generate the ass files
        """
        deadline_node = hou.node(self.data["node_path"])
        self.logger.info(f"Caching frame range: {self.start}-{self.end}")

        arnold_rops = hou_utils.input_nodes_of_type(deadline_node, ["arnold"])

        # work out the total to generate progress
        frame_count = self.end - self.start
        self.total = frame_count * len(arnold_rops)

        for arnold_rop in arnold_rops:
            render_path = arnold_rop.parm("ar_picture").eval()
            file_utils.create_directories(os.path.dirname(render_path))

            # override the frame range if selected
            arnold_rop.parm("trange").set(1)
            hou_utils.set_rop_frame_range(arnold_rop, self.start, self.end)

            # add the callback to track the progress of the ass gene
            arnold_rop.addRenderEventCallback(self.ass_file_progress)

            # render the ass files
            ass_path = arnold_rop.parm("ar_ass_file").eval()
            file_utils.create_directories(os.path.dirname(ass_path))

            ass_sequence = sequence_utils.convert_frame_to_sequence(ass_path)
            self.logger.info(f"Generating asses...{ass_sequence}")
            arnold_rop.parm("execute").pressButton()
        self.logger.info("Complete")


if __name__ == "__main__":
    exporter = AssExporter()
    metadata_file = sys.argv[1]
    exporter.start = int(sys.argv[2])
    exporter.end = int(sys.argv[3])
    exporter.batch_process(metadata_file)
