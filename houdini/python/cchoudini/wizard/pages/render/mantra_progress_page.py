""" Submit renders to the farm page """
import os
import hou
import cccore.deadline.submit as submit
import cccore.utils.file_utils as file_utils
import cccore.core_constants as core_constants
import cchoudini.hou_constants as hou_constants
from cchoudini.wizard.pages.render.render_progress_page import RenderProgressPage

# constants
ROP_TYPE_TO_PICTURE_PARM = hou_constants.ROP_TYPE_TO_PICTURE_PARM


class MantraProgressPage(RenderProgressPage):
    title = "Mantra Progress Page"
    subtitle = "Submitting Mantra Render Nodes"

    def __init__(self, parent=None):
        super().__init__(parent)

    def submit_renders(self):
        """
        Submit a tile render
        """
        progress = 20
        self.set_value(progress)

        # loop through all inputs
        node_submit_size = 60 / len(self.render_rops)

        # submit arnold jobs
        for rop in self.render_rops:
            node_type_name = rop.type().name()
            if node_type_name in ["ifd", "karma"]:
                self.create_mantra_karma_job(rop)

            progress += node_submit_size
            self.set_value(progress)

    def create_mantra_karma_job(self, rop):
        # type: (hou.Node) -> None
        """
        Create a mantra job for the arnold rop

        Args:
            rop: Mantra ROP node to render
        """
        node_type_name = rop.type().name()
        picture_parm = ROP_TYPE_TO_PICTURE_PARM[node_type_name]
        if node_type_name == "ifd":
            submit_cls = submit.MantraRenderDeadlineSubmit
            job_type = self.MANTRA_RENDER
        else:
            submit_cls = submit.KarmaRenderDeadlineSubmit
            job_type = self.KARMA_RENDER

        # save sequences
        output_path = rop.parm(picture_parm).eval()
        self.sequences.append(output_path)

        # get the rop name for the job name
        frame_range = self.data["frame_range"]
        self.data["rop_path"] = rop.path()
        rop_name = f"{node_type_name.title()} Node: {rop.name()} {frame_range}"
        self.add_message(rop_name)

        # get output path information
        output_dir = os.path.dirname(output_path)
        file_utils.create_directories(output_dir)

        # create jobs directory
        job_info_dict = {"Name": rop_name,
                         "ChunkSize": self.data["ass_chunk_size"],
                         "Frames": self.data["frame_range"],
                         "Pool": self.data["ass_pool"],
                         "Priority": self.data["ass_priority"]
                         }

        plugin_info_dict = {"Arguments": self.data_file_path,
                            "NodePath": rop.path()
                            }

        self.custom_dict = {"prefix": self.prefix,
                            "batch_name": self.batch_name
                            }

        # standard non-tile render
        if not self.data["tile_rendering"]:
            mantra_karma_job = submit_cls(job_info_dict,
                                          plugin_info_dict,
                                          self.custom_dict
                                          )

            # add as a dependency to the main job
            mantra_karma_id = mantra_karma_job.submit_job()
            self.batch_name = mantra_karma_job.batch_name
            self.add_submit_data(mantra_karma_id, job_type)
            self.add_message(f"Job Id: {mantra_karma_id}")
        else:
            start = self.data["start"]
            end = self.data["end"]
            plugin_info_dict["is_tile"] = True
            tile_count = self.data["tile_x"] * self.data["tile_y"]

            for frame_num in range(start, end + 1):
                # create the tile job dictionary
                job_name = f"Render Node: {rop.name()} - Frame: {frame_num}"
                job_info_dict["Name"] = job_name
                job_info_dict["TileJob"] = True
                job_info_dict["TileJobFrame"] = frame_num
                job_info_dict["TileJobTileCount"] = tile_count

                # submit the arnold deadline job
                mantra_karma_job = submit_cls(job_info_dict,
                                              plugin_info_dict,
                                              self.custom_dict
                                              )
                # add as a dependency to the main job
                mantra_karma_id = mantra_karma_job.submit_job()
                self.batch_name = mantra_karma_job.batch_name
                self.custom_dict["batch_name"] = self.batch_name
                self.add_submit_data(mantra_karma_id, self.KARMA_RENDER_TILE)
                self.add_message(f"Job Id: {mantra_karma_id}")

                # create tile assembling dictionaries and job
                tile_job_info_dict = {"Name": job_name, "Pool": "nuke"}
                frame_arg = f"{core_constants.FRAME_PREFIX}{frame_num}"
                tile_plugin_info_dict = {"output_path": output_path,
                                         "frame_num": frame_arg,
                                         "ass_path": str()
                                         }

                # set the nuke environment variables
                # it will work for the deadline job
                self.submit_tile_assembler(
                    mantra_karma_id, tile_job_info_dict, tile_plugin_info_dict
                )
