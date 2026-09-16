"""
Exporter to create caches
"""
import hou
import sys
from typing import Optional
import ccgeneral.exporter.base_exporter as base_exporter
from cchoudini.node.cccache import No8CacheNode
from cchoudini.node.ccwedger import No8WedgerNode
import cccore.utils.file_utils as file_utils


class CacheExporter(base_exporter.BaseExporter):
    """
    Generate cache in batch mode
    """
    POST_CACHE_FRAME = "houdini/python/cchoudini/utils/post_cache_frame.py"

    def __init__(self, start=None, end=None):
        # type: (Optional[int], Optional[int]) -> None
        """
        Args:
            start: The first frame
            end: The last frame
        """
        super(CacheExporter, self).__init__()
        self.start = start
        self.end = end
        self.cc_cache_node = None
        self.callback_cache_path = str()

    def open_file(self):
        """
        Load the hip file
        """
        wip_file_path = self.data["wip_file_path"]
        self.logger.info(f"Opening...{wip_file_path}")
        hou.hipFile.load(wip_file_path,
                         suppress_save_prompt=True,
                         ignore_load_warnings=True
                         )

    def set_wedger_node(self):
        """
        Set the wedger node values
        """
        # set the value for a wedge
        cc_wedger_node = No8CacheNode(self.cc_cache_node).cc_wedger_node
        if not cc_wedger_node:
            return

        ccwedger_inst = No8WedgerNode(cc_wedger_node)
        wedge_value = self.data["wedge_value"]

        # dealing with vector list
        if " " in wedge_value:
            value_to_set = wedge_value.split(" ")
            value_to_set.remove("")
        else:
            value_to_set = wedge_value
        ccwedger_inst.set_input_value(value_to_set)

        # update cccache node for wedge name
        self.cc_cache_node.parm("cache_name").set(self.data["new_cache_name"])

    def create_frame_post_process_callback(self):
        """
        Run the script that removes ass files

        Return:
            cleanup_path: Path of the post process script
        """
        # read the template of the cleanup script
        template_frame_cache_path = self.project_data.get_relative_path(self.POST_CACHE_FRAME)
        post_frame_txt = file_utils.read_file(template_frame_cache_path)
        output_path = self.cc_cache_node.parm("output_path").eval()

        # replace the data with the rs sequence
        post_frame_txt = post_frame_txt.replace("CACHE_PATH", output_path)
        post_frame_txt = post_frame_txt.replace("START_FRAME", str(self.start))
        post_frame_txt = post_frame_txt.replace("END_FRAME", str(self.end))

        cache_frame_name = f"{self.cc_cache_node.name()}_cache_frame_callback.py"
        self.callback_cache_path = file_utils.join_from_list([self.project_data.appdata, cache_frame_name])

        # write cleanup file
        file_utils.write_file(self.callback_cache_path, post_frame_txt)
        self.logger.info(f"Written post process: {self.callback_cache_path}")

    def set_post_frame_script(self):
        """
        Create and set the post process script
        for outputting the caching progress
        """
        self.create_frame_post_process_callback()
        self.cc_cache_node.parm("tpostframe").set(1)
        self.cc_cache_node.parm("postframe").set(self.callback_cache_path)
        self.cc_cache_node.parm("lpostframe").set("python")

    def export(self):
        """
        Loop through the connected arnold ROPs
        and generate the ass files
        """
        node_path = self.data["node_path"]
        self.logger.info(f"Node Path: {node_path}")
        self.cc_cache_node = hou.node(node_path)
        self.logger.info(f"Cache Node...{self.cc_cache_node}")

        self.set_post_frame_script()
        cache_type = self.cc_cache_node.parm("cache_type").evalAsString()
        self.logger.info(f"Cache type...{cache_type}")

        # set the value for a wedge
        self.set_wedger_node()
        No8CacheNode(self.cc_cache_node).submit_cache_local(start=self.start, end=self.end)
        self.logger.info("Complete")


if __name__ == "__main__":
    metadata_path = sys.argv[1]
    try:
        start_frame = sys.argv[2]
        end_frame = sys.argv[3]
    except IndexError:
        start_frame = None
        end_frame = None
    exporter = CacheExporter(start=start_frame, end=end_frame)
    exporter.batch_process(metadata_path)

