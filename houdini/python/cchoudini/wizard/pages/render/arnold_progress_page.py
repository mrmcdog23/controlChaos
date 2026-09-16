""" Submit renders to the farm page """
import os
import hou
import cccore.deadline.submit as submit
import cccore.utils.sequence_utils as sequence_utils
import cccore.utils.file_utils as file_utils
import cccore.core_constants as core_constants
import cchoudini.utils.hou_utils as hou_utils
from cchoudini.wizard.pages.render.render_progress_page import RenderProgressPage
import cchoudini.render.create_render_jobs as submit_arnold_render


class ArnoldProgressPage(RenderProgressPage):
    title = "Arnold Progress Page"
    subtitle = "Submitting Arnold Render Nodes"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ass_job_id = str()
        self.ass_frame_range = int()

    def submit_renders(self):
        """
        Submit a tile render
        """
        progress = 20
        self.set_value(progress)
        node_submit_size = 60 / len(self.render_rops)

        if self.data["range_type"] == "Node Range":
            # get the arnold ass frame range
            arnold_rops = hou_utils.input_nodes_of_type(self.deadline_node, ["arnold"])
            if arnold_rops:
                self.ass_frame_range = hou_utils.get_maximum_frame_range_for_ass_job(arnold_rops)
        else:
            self.ass_frame_range = self.data["frame_range"]

        # submit arnold jobs
        renderlayer_names = self.data["renderlayer_names"]
        for rop in self.render_rops:
            # skip if render layer is not selected
            if rop.name() not in renderlayer_names:
                continue

            node_type_name = rop.type().name()
            if node_type_name == "arnold":
                self.create_arnold_job(rop)

            progress += node_submit_size
            self.set_value(progress)

    def generate_ass_job(self):
        # type: () -> str
        """
        Create generate the ass file job

        Returns:
            ass_job_id: The submitted job id
        """
        renderlayer_names = self.data["renderlayer_names"]
        arnold_rops = ", ".join(renderlayer_names)
        gen_ass_job = submit_arnold_render.create_ass_job(
            self.deadline_node,
            self.ass_frame_range,
            self.metadata_file_path,
            self.prefix,
            chunk_size=self.data.get("ass_chunk_size"),
            priority=self.data.get("ass_priority"),
            arnold_rops=arnold_rops
        )
        ass_job_id = gen_ass_job.submit_job()
        self.batch_name = gen_ass_job.batch_name
        self.custom_dict["batch_name"] = self.batch_name
        self.add_submit_data(ass_job_id, self.ASS_GENERATE)
        return ass_job_id

    def override_node_frame_range(self, arnold_rop):
        # type: (hou.Node) -> None
        """
        If the frame range is set to node override it in the data
        """
        if self.data["range_type"] != "Node Range":
            self.logger.info(f"Frame range set!")
            return

        # account for random frame ranges
        random_frames_value = hou_utils.get_random_frames_value(arnold_rop)
        if random_frames_value:
            self.data["frame_range"] = random_frames_value
            return

        # get the overriding frame range from the frame range node
        output_node = arnold_rop.outputs()[0]
        if output_node.type().name() == "frame_range":
            self.logger.info("Getting the override frame range node")
            start, end = hou_utils.get_frame_range(
                output_node, start_parm="fx", end_parm="fy")
        else:
            # get the overriding frame range from the node
            start, end = hou_utils.get_frame_range(arnold_rop)

        # set the start and end frame
        self.logger.info(f"Overriding frame range: {start}-{end}")
        self.data["start"] = start
        self.data["end"] = end

        # set in the dictionary its values
        if start == end:
            self.data["frame_range"] = str(start)
        else:
            self.data["frame_range"] = f"{start}-{end}"
        self.logger.info(f"frame_range: {self.data['frame_range']}")

    def create_arnold_job(self, arnold_rop):
        # type: (hou.Node) -> None
        """
        Create an arnold job for the arnold rop

        Args:
            arnold_rop: Arnold ROP node to render
        """
        # run the paths
        self.override_node_frame_range(arnold_rop)

        if not self.ass_job_id:
            self.ass_job_id = self.generate_ass_job()

        rop_name = arnold_rop.name()
        ass_path = arnold_rop.parm("ar_ass_file").eval()
        self.add_message(f"Ass Path: {ass_path}")

        # save sequences
        output_path = arnold_rop.parm("ar_picture").eval()
        self.sequences.append(output_path)

        # get output path information
        output_dir = os.path.dirname(output_path)
        file_utils.create_directories(output_dir)
        self.add_message(f"Output directory: {output_dir}")
        output_sequence = sequence_utils.convert_frame_to_sequence(output_path)
        plugin_info_dict = {"InputFile": ass_path, "FrameRange": self.data["frame_range"]}

        # create jobs directory
        job_info_dict = {"OutputDirectory0": os.path.dirname(output_sequence),
                         "OutputFilename0": os.path.basename(output_sequence),
                         "AddEnvironment": False,
                         "IsFrameDependent": True,
                         "ChunkSize": self.data["render_chunk_size"],
                         "Frames": self.data["frame_range"],
                         "Pool": self.data["render_pool"],
                         "Priority": self.data["render_priority"],
                         "TileJob": self.data["tile_rendering"],
                         "TileJobTilesInX": self.data["tile_x"],
                         "TileJobTilesInY": self.data["tile_y"]
                         }

        if not self.data["tile_rendering"]:
            frame_range = self.data["frame_range"]
            job_name = f"Arnold Node: {rop_name} - {frame_range}"
            job_info_dict["Name"] = job_name
            arnold_job = submit.ArnoldDeadlineSubmit(job_info_dict,
                                                     plugin_info_dict,
                                                     self.custom_dict
                                                     )

            # add as a dependency to the main job
            arnold_job.add_dependencies(self.ass_job_id, self.batch_name)
            arnold_id = arnold_job.submit_job()
            self.add_submit_data(arnold_id, self.ARNOLD_KICK)
            self.add_message(f"Job Id: {arnold_id}")

        else:
            start = self.data["start"]
            end = self.data["end"]
            for frame_num in range(start, end + 1):
                # create the tile job dictionary
                job_name = f"Arnold Node: {rop_name} - Frame: {frame_num}"
                job_info_dict["Name"] = job_name
                job_info_dict["TileJobFrame"] = frame_num

                # change plugin args for tile rendering
                plugin_info_dict["SingleRegionFrame"] = int(frame_num)
                plugin_info_dict["RegionJob"] = True
                plugin_info_dict["SingleAss"] = True

                # calculate the region dictionary
                region_args = self.get_arnold_region_args(self.data["tile_x"],
                                                          self.data["tile_y"],
                                                          arnold_rop,
                                                          frame_num
                                                          )
                plugin_info_dict.update(region_args)

                # submit the arnold deadline job
                arnold_job = submit.ArnoldDeadlineSubmit(job_info_dict,
                                                         plugin_info_dict,
                                                         self.custom_dict
                                                         )
                # add as a dependency to the main job
                arnold_job.add_dependencies(self.ass_job_id, self.batch_name)
                arnold_id = arnold_job.submit_job()
                self.add_submit_data(arnold_id, self.ARNOLD_KICK_TILE)
                self.add_message(f"Job Id: {arnold_id}")

                # create tile assembling dictionaries and job
                tile_job_info_dict = {
                    "Name": job_name,
                    "Pool": "nuke",
                    "ExternalSubmit": True
                }
                frame_arg = f"{core_constants.FRAME_PREFIX}{frame_num}"
                tile_plugin_info_dict = {
                    "output_path": output_path,
                    "frame_num": frame_arg,
                    "ass_path": ass_path
                }

                # set the nuke environment variables
                # it will work for the deadline job
                self.submit_tile_assembler(
                    arnold_id, tile_job_info_dict, tile_plugin_info_dict
                )

    @staticmethod
    def get_arnold_region_args(tile_x, tile_y, arnold_rop, frame_num):
        # type: (int, int, hou.Node, int) -> dict
        """
        Work out the arnold region tiles as an argument dictionary

        Args:
            tile_x: The x tile value
            tile_y: The y tile value
            arnold_rop: The arnold rop node
            frame_num: The frame number to create tiles for

        Returns:
            region_args: The region arguments dictionary
        """
        output_path = arnold_rop.parm("ar_picture").eval()
        cam = arnold_rop.parm("camera").evalAsNode()
        res_x = cam.parm("resx").eval()
        res_y = cam.parm("resy").eval()

        chunk_x = res_x / tile_x
        chunk_y = res_y / tile_y

        region_num = 0
        region_args = dict()
        for x in range(0, tile_x):
            for y in range(0, tile_y):
                start_x = x * chunk_x
                end_x = (x + 1) * chunk_x
                start_y = y * chunk_y
                end_y = (y + 1) * chunk_y

                region_args[f"RegionLeft{region_num}"] = start_x
                region_args[f"RegionRight{region_num}"] = end_x
                region_args[f"RegionBottom{region_num}"] = end_y
                region_args[f"RegionTop{region_num}"] = start_y

                # get filename and work out the region names
                directory = os.path.dirname(output_path)
                filename = file_utils.get_file_name(output_path)
                _, extension = os.path.splitext(output_path)
                region_filename = f"{filename}_{frame_num}_{region_num}{extension}"
                region_path = os.path.join(directory, region_filename)

                region_args[f"RegionFilename{region_num}"] = region_path
                region_num += 1

        return region_args
