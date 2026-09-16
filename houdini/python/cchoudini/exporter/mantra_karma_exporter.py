"""
Create render files from karma or mantra ROP
"""
import hou
import sys
import os
import ccgeneral.exporter.base_exporter as base_exporter
import cccore.utils.sequence_utils as sequence_utils
import cccore.utils.file_utils as file_utils
import cchoudini.utils.hou_utils as hou_utils


class MantraExporter(base_exporter.BaseExporter):
    def __init__(self):
        super(MantraExporter, self).__init__()
        self.start = int()
        self.end = int()
        self.total = int()
        self.node_path = str()
        self.rop_node = None
        self.tile_number = None
        self.created = 0
        self.picture_parm = str()
        self.render_parm = str()
        self.enable_tiling = str()
        self.tile_count_x = str()
        self.tile_count_y = str()
        self.render_tile_index = str()

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

    @property
    def tile_x(self):
        """
        Number of tiles in the X axis
        """
        return self.data["tile_x"]

    @property
    def tile_y(self):
        """
        Number of tiles in the Y axis
        """
        return self.data["tile_y"]

    @property
    def is_mantra(self):
        # type: () -> bool
        """
        Is it a mantra render
        """
        return self.rop_node.type().name() == "ifd"

    def set_parameter_names(self):
        """
        Set the parameter names based on the rop type
        """
        if self.is_mantra:
            # mantra node type
            self.picture_parm = "vm_picture"
            self.render_parm = "execute"
            self.enable_tiling = "vm_tile_render"
            self.tile_count_x = "vm_tile_count_x"
            self.tile_count_y = "vm_tile_count_y"
            self.render_tile_index = "vm_tile_index"
        else:
            # karma node type
            self.picture_parm = "picture"
            self.render_parm = "render"
            self.enable_tiling = "husk_tile"
            self.tile_count_x = "husk_tilecount1"
            self.tile_count_y = "husk_tilecount2"
            self.render_tile_index = "husk_tileindex"

    def set_node_for_tile_render(self):
        """
        Set the individual tile count and index
        """
        self.logger.info(f"Rendering tile number: {self.tile_number}")
        self.logger.info(f"Setting: {self.tile_x} {self.tile_y} {self.rop_node}")

        # set the render node tile parameters
        self.rop_node.parm(self.enable_tiling).set(1)
        self.rop_node.parm(self.tile_count_x).set(self.tile_x)
        self.rop_node.parm(self.tile_count_y).set(self.tile_y)
        self.rop_node.parm(self.render_tile_index).set(self.tile_number)

        # if it is a karma node remove the suffix
        if not self.is_mantra:
            self.rop_node.parm("husk_tilesuffix").set("")

        # work out and set the output path
        output_path = self.rop_node.parm(self.picture_parm).eval()
        self.logger.info(f"Output Path...{output_path}")
        directory = os.path.dirname(output_path)
        filename = file_utils.get_file_name(output_path)
        _, extension = os.path.splitext(output_path)
        region_filename = f"{filename}_{self.start}_{self.tile_number}{extension}"
        region_path = os.path.join(directory, region_filename)
        self.logger.info(f"Region Path...{region_path}")

        # break any expression and set the region path
        self.rop_node.parm(self.picture_parm).deleteAllKeyframes()
        self.rop_node.parm(self.picture_parm).set(region_path)

    def export(self):
        """
        Loop through the connected arnold ROPs
        and generate the ass files
        """
        self.rop_node = hou.node(self.node_path)
        self.logger.info(f"Caching frame range: {self.start}-{self.end}")
        self.set_parameter_names()

        # work out the total to generate progress
        self.logger.info(f"ROP Node: {self.rop_node}")
        render_path = self.rop_node.parm(self.picture_parm).eval()
        file_utils.create_directories(os.path.dirname(render_path))

        # override the frame range if selected
        self.rop_node.parm("trange").set(1)
        hou_utils.set_rop_frame_range(self.rop_node, self.start, self.end)

        # run the tile render settings
        if self.tile_number is not None:
            self.set_node_for_tile_render()
        else:
            # render the single frame files
            output_path = self.rop_node.parm(self.picture_parm).eval()
            file_utils.create_directories(os.path.dirname(output_path))
            sequence_path = sequence_utils.convert_frame_to_sequence(output_path)
            self.logger.info(f"Generating render...{sequence_path}")

        # run the render
        self.rop_node.parm(self.render_parm).pressButton()
        self.logger.info("Complete")


if __name__ == "__main__":
    exporter = MantraExporter()
    metadata_file = sys.argv[1]
    exporter.node_path = sys.argv[2]
    exporter.start = int(sys.argv[3])
    exporter.end = int(sys.argv[4])
    try:
        exporter.tile_number = int(sys.argv[5])
    except IndexError:
        pass
    exporter.batch_process(metadata_file)
