""" Exporter for building shots publishing """
import os
import sys
import hou
import cccore.utils.file_utils as file_utils
import cccore.utils.sequence_utils as sequence_utils
import cccore.data.server_data as server_data
import cchoudini.render.create_render_jobs as create_render_jobs
import cchoudini.hou_constants as hou_constants
import cchoudini.utils.hou_utils as hou_utils
from ccgeneral.exporter.base_exporter import BaseExporter
from cchoudini.shot.switch_to_shot import SwitchToShot


class BuildShotsExporter(BaseExporter):
    """
    Exporter to create and publish a Houdini Digital Asset
    """
    def __init__(self):
        super().__init__()
        self.project_data = server_data.ProjectData()
        self.total_progress = 0
        self.job_ids = list()
        self.full_shot_list = str()
        self.template_file = str()
        self.built_paths = list()
        self.metadata_file_path = str()
        self.master_episode_name = str()
        self.task_name = str()
        self.render_shots = list()
        self.publish_shots_list = list()

    def export(self):
        """
        Export the asset and publish it to ftrack
        """
        self.set_class_variables()
        self.build_and_render_shots()

    def set_class_variables(self):
        """
        Set the class variables from the data
        """
        self.add_deadline_progress(10)
        self.template_file = self.data["template_file"]
        self.master_episode_name = self.data["master_episode_name"]
        self.task_name = self.data["save_task_name"]
        self.render_shots = self.data["render_shots"]
        self.publish_shots_list = self.data["publish_shots_list"]
        self.metadata_file_path = self.data["metadata_file_path"]

    def add_deadline_progress(self, adding_progress):
        # type: (int) -> None
        """
        Add to progress and log it for farm progress

        Args:
            adding_progress: Value to add
        """
        self.total_progress += adding_progress
        self.logger.info(f"Progress: {int(self.total_progress)}%")

    def build_and_render_shots(self):
        """
        Main function for building and rendering shots
        """
        num_of_shots = len(self.publish_shots_list)
        progress_chunk_size = (50 / num_of_shots) / 2

        for seq_shot_name in self.publish_shots_list:
            self.seq_shot_name = seq_shot_name
            self.add_deadline_progress(progress_chunk_size)

            self.build_shot()
            self.submit_render_shot()

            self.add_deadline_progress(progress_chunk_size)
            self.logger.info(f"Progress: {int(self.total_progress)}%")

        # add the shot list to the metadata file
        self.data["slack_message_text"] = "\n".join(self.built_paths)
        file_utils.write_json(self.metadata_file_path, self.data)

    def submit_render_shot(self):
        """
        Submit the job to the farm it in the render shots list
        """
        if self.seq_shot_name not in self.render_shots:
            return
        self.update_render_data()
        self.submit_ass_files()
        self.submit_arnold_renders()
        self.submit_publish_job()

    def save_data_to_json(self):
        # type: () -> str
        """
        Save the data to a json file to run as an arg

        Returns:
            metadata_path: Path to metadata file
        """
        metadata_path = file_utils.temp_file_path("ass_file_data", "metadata")
        file_utils.write_json(metadata_path, self.data)
        return metadata_path

    def build_shot(self):
        """
        Build the shot through opening the template
        and swapping the assets
        """
        sequence_name, shot_name = self.seq_shot_name.split("_")
        switch_shot_list = SwitchToShot(
            self.master_episode_name,
            sequence_name,
            shot_name,
            self.task_name,
            template_file=self.template_file,
            ftshot=self.ftshot,
            save=True
        )
        self.built_paths.append(switch_shot_list.hou_file_path)

    def update_render_data(self):
        """
        Set the deadline node and build list of sequences to render
        """
        out_node = hou.node("/out")
        self.deadline_node = hou_utils.find_all_subnodes_of_types(out_node, ["ccsubmit"])[0]
        render_rops = hou_utils.input_nodes_of_type(self.deadline_node, hou_constants.RENDER_NODE_TYPES)

        # from the rops build the sequence list
        file_sequences = list()
        for arnold_rop in render_rops:
            output_path = arnold_rop.parm("ar_picture").eval()
            sequence_path = sequence_utils.convert_frame_to_sequence(output_path)
            file_sequences.append(sequence_path)
        self.data["file_sequences"] = file_sequences

    def submit_ass_files(self):
        """
        Submit the ass file job to the farm
        """
        current_start, current_end = hou.playbar.frameRange()

        # set the individual ass job render
        self.data["start"] = int(current_start)
        self.data["end"] = int(current_end)
        self.data["wip_file_path"] = hou.hipFile.name()
        self.data["node_path"] = self.deadline_node.path()

        # save backup file and data
        file_path = hou.hipFile.basename()
        self.data_file_path = self.save_data_to_json()
        self.data["metadata_file_path"] = self.data_file_path
        self.prefix, _ = os.path.splitext(file_path)

        # get the shot frame range
        ass_frame_range = f"{int(current_start)}-{int(current_end)}"
        gen_ass_job = create_render_jobs.create_ass_job(
            self.deadline_node,
            ass_frame_range,
            self.data_file_path,
            self.prefix,
            username=self.data["artist_name"]
        )
        self.ass_job_id = gen_ass_job.submit_job()
        self.logger.info(f"Submitted ass job: {self.ass_job_id}")
        self.batch_name = gen_ass_job.batch_name
        self.job_ids.append(self.ass_job_id)

    def submit_arnold_renders(self):
        """
        Submit the arnold render to the farm
        """
        render_rops = hou_utils.input_nodes_of_type(self.deadline_node, hou_constants.RENDER_NODE_TYPES)
        for arnold_rop in render_rops:
            arnold_job = create_render_jobs.create_arnold_job(
                arnold_rop,
                self.ass_job_id,
                self.batch_name,
                self.prefix,
                username=self.data["artist_name"]
            )
            arnold_id = arnold_job.submit_job()
            self.logger.info(f"Arnold job: {arnold_id}")
            self.job_ids.append(arnold_id)

    def submit_publish_job(self):
        """
        Submit the project to ftrack job if set
        """
        self.data["metadata_file_path"] = self.data_file_path
        file_utils.write_json(self.data_file_path, self.data)

        publish_job = create_render_jobs.create_publish_job(
            self.prefix,
            self.data_file_path,
            self.job_ids,
            self.batch_name,
            username=self.data["artist_name"]
        )
        publish_job_id = publish_job.submit_job()
        self.logger.info(f"Publish job: {publish_job_id}")


if __name__ == "__main__":
    exporter = BuildShotsExporter()
    exporter.batch_process(sys.argv[1])
