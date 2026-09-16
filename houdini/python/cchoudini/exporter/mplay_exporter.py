""" Publish mplayer image sequences """
import os
import hou
import sys
import ccftrack.publish as publish
import cccore.file_env.context as context
import cccore.utils.sequence_utils as sequence_utils
import cccore.utils.file_utils as file_utils
from ccgeneral.exporter.base_exporter import BaseExporter


class MPlayExporter(BaseExporter):
    """ Exporter to create and publish a flipbook """
    def __init__(self):
        super().__init__()
        self.publish_sequence_path = str()
        self.version_int = int()
        self.seq_data = None

    def export(self):
        """
        Export the asset and publish it to ftrack
        """
        self.initialize_ftrack()
        self.copy_flipbook_image_sequence()
        self.publish_to_ftrack()
        self.remove_original_flipbook()

    @property
    def flipbook_source_path(self):
        # type: () -> str
        """
        The source flipbook path
        """
        hip_name = file_utils.get_file_name(self.data["wip_file_path"])
        flipbook_name = f"{hip_name}.####.jpg"

        # use the context to get the directory
        ctx = context.Context()
        flipbook_path = file_utils.join_from_list(
            ctx.flipbook_dir, hip_name, flipbook_name)
        return flipbook_path

    @BaseExporter.add_to_percentage(40)
    def copy_flipbook_image_sequence(self):
        """
        Copy the original sequence to publish location
        """
        # get publish sequence path component
        self.data["aov"] = "flipbook"
        self.data["ext"] = "jpg"
        self.data["subfolder"] = "flipbook"

        self.seq_data = sequence_utils.get_sequence_data(self.flipbook_source_path)

        # add using the context get the path
        ctx = context.Context(overrides=self.data)
        ctx.use_next_sequence_version()

        use_version = self.ftquery.get_correct_version(ctx.sequence_path)
        self.log(f"Use sequence version: {use_version}")

        ctx.use_version = use_version
        self.publish_sequence_path = ctx.sequence_path
        self.log(f"Copying : {self.flipbook_source_path} to {self.publish_sequence_path}")

        # copy the sequence to publish location
        self.version_int = use_version
        sequence_utils.copy_sequence(self.flipbook_source_path, self.publish_sequence_path)

    @property
    def mov_path(self):
        # type: () -> str
        """ Construct the movie path to export """
        self.data["ext"] = "mov"
        self.data["subfolder"] = "video"
        ctx = context.Context(overrides=self.data)
        ctx.use_is_single_frame_sequence = True
        ctx.use_version = self.version_int
        return ctx.sequence_path

    @BaseExporter.add_to_percentage(30)
    def publish_to_ftrack(self):
        """
        Publish the flipbook to FTrack
        """
        self.data["file_sequences"] = [self.publish_sequence_path]
        self.data["playable_component"] = self.publish_sequence_path
        self.data["version_num"] = self.version_int
        self.data["mov_path"] = self.mov_path
        self.data["keep_mov"] = True

        # publish the flipbook render
        self.log(f"Publishing version {self.version_int} to FTrack...")
        ftrack_pub_inst = publish.FtrackPublish(self.data)
        id_ = ftrack_pub_inst.asset_version["id"]
        self.log(f"Asset Version: {id_}")

    @BaseExporter.add_to_percentage(30)
    def remove_original_flipbook(self):
        """
        Remove the original flipbook sequence to the
        same one does not get published twice
        """
        for frame_path in self.seq_data.frame_paths:
            if os.path.exists(frame_path):
                os.remove(frame_path)
                self.logger.info(f"Removing: {frame_path}")
        self.log("Flipbook publish complete..")


if __name__ == "__main__":
    exporter = MPlayExporter()
    exporter.batch_process(sys.argv[1])