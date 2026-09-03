""" ftrack publish file to create asset versions """
import os
import sys
import ccftrack.asset_version as asset_version
import ccftrack.shot as shot
import ccftrack.asset as asset
import cccore.utils.ffmpeg_utils as ffmpeg_utils
import cccore.utils.file_utils as file_utils
import cccore.utils.cc_logging as cc_logging
import cccore.utils.sequence_utils as sequence_utils
import cccore.file_env.context_utils as context_utils
import cccore.core_constants as core_constants
import cccore.data.server_data as server_data


class FtrackPublish(object):
    """
    Publish an asset or sequence to ftrack
    """
    def __init__(self, data):
        # type: (dict) -> None
        """
        Args:
            data: Publish information dictionary
        """
        self.data = data
        self.sequence_only = True
        self.asset_version = None
        self.movie_name = str()

        # movie component found
        self.logger = cc_logging.cc_logger()
        self.image_sequence = self.data.get("playable_component")
        self.ftver = asset_version.FtAssetVersion()
        self.ftshot = shot.FtShot(session=self.ftver.session)
        self.ftasset = asset.FtAsset(session=self.ftver.session)
        self.project_data = server_data.ProjectData()

        # run functions
        self.create_thumbnail()
        self.create_asset_version()
        self.publish_render_component()
        self.publish_additional_components()
        self.create_ftrack_movie()

    @property
    def playable_component(self):
        playable_component = self.data.get("playable_component")
        if playable_component:
            return playable_component
        file_sequences = self.data.get("file_sequences")
        if file_sequences:
            return file_sequences[0]

    def get_category(self, ext):
        # type: (str) -> str
        """
        Get the correct category for publishing

        Args:
            ext: The file extension to use

        Returns:
            category: The category type to publish under
        """
        # if there are file sequences use that extension
        if self.data.get("file_sequences"):
            file_sequence = self.data["file_sequences"][0]
            ext = file_utils.get_extension(file_sequence)

        category = file_utils.get_category(ext)
        self.logger.info(f"Publishing file type {ext} as {category}")
        return category

    def create_thumbnail(self):
        """
        If a thumbnail has not been set try and create one
        """
        self.logger.info("Generating thumbnail...")
        # if already set then no need to create one
        thumbnail_path = self.data.get("thumbnail_path")
        if thumbnail_path:
            self.logger.info(f"Thumbnail found: {thumbnail_path}")
            return

        # if not file sequences then can not create one
        file_sequences = self.data.get("file_sequences")
        if not file_sequences:
            self.logger.warning("No files sequence to publish")
            return

        # find an image sequence from the file sequences
        image_sequence_path = None
        image_types = tuple(core_constants.IMAGE_TYPES)
        for file_sequence in file_sequences:
            if file_sequence.endswith(image_types):
                image_sequence_path = file_sequence
                break

        # if there is no image
        if not image_sequence_path:
            self.logger.warning("No image sequence sequence to publish")
            return

        # if a png is found then use that as the thumbnail
        if image_sequence_path.endswith(".png"):
            self.data["thumbnail_path"] = image_sequence_path
            return

        # create a png file from the image to use as a thumbnail
        file_name = file_utils.get_file_name(image_sequence_path)
        self.logger.info(f"Image sequence path: {image_sequence_path}")
        output_path = file_utils.temp_file_path(file_name, "png", sub_dir="thumbnail")
        file_utils.create_directory(output_path)

        # find first path
        seq_data = sequence_utils.get_sequence_data(image_sequence_path)
        first_frame_path = seq_data.frame_paths[0]

        # run ffmpeg conversion to png
        ffmpeg_utils.convert_image_type(first_frame_path, output_path)
        self.logger.info(f"Generated...{output_path}")
        self.data["thumbnail_path"] = output_path

        # if not image sequence then use the first one
        if not self.playable_component:
            self.logger.info(f"Using output path: {self.playable_component}")
            self.playable_component = self.playable_component

    def create_asset_version(self):
        """
        Create the new file version
        """
        self.logger.info("Creating new asset version on Ftrack...")

        # set the extension in the data
        wip_file_path = self.data.get('wip_file_path')
        if wip_file_path:
            ext = file_utils.get_extension(wip_file_path)
            self.data["ext"] = ext
            self.data["category"] = self.get_category(ext)
        else:
            self.data["pub_file_path"] = self.image_sequence

        # create and set the asset version
        if self.data.get("asset_build_name"):
            ftrack_class = self.ftasset
            self.movie_name = self.data["asset_build_name"]
        else:
            ftrack_class = self.ftshot
            self.movie_name = self.data["shot_name"]

        # set the asset data
        self.logger.info("Creating asset version.....")
        self.asset_version = ftrack_class.set_ftrack_data(self.data)

        av_id = self.asset_version["id"]
        self.logger.info(f"Asset Version: {av_id}")
        self.ftver.asset_version_id = av_id

        # log the url for extraction
        self.logger.info(f"Version url: {self.ftver.asset_version_url}")

        # add to the metadata path if it exists
        self.data["asset_version_url"] = self.ftver.asset_version_url

        file_utils.update_metadata_file(self.data)

    def publish_render_component(self):
        """
        Add the rendered frames as a component
        """
        if not self.data.get("file_sequences"):
            self.logger.warning(f"No file sequences to publish")
            return

        component_names = self.ftver.component_to_path
        self.logger.info(f"Publishing version {self.ftver.version_int}")

        for index, sequence_path in enumerate(self.data["file_sequences"]):
            self.logger.info(f"Sequence: {sequence_path}")
            seq_data = sequence_utils.get_sequence_data(sequence_path)
            sequence_utils.make_sequence_read_only(sequence_path)
            ctx = context_utils.get_context_from_path(sequence_path)

            # get the aov name from the context or index
            aov_name = "main"
            name_to_path = {aov_name: seq_data.padded_path}
            self.ftver.add_component_dict(name_to_path)

    def publish_additional_components(self):
        """
        Add any additional components to the asset version
        """
        additional_components = self.data.get("additional_components")
        if not additional_components:
            return

        # add additional components
        for component_name, source_path in additional_components.items():
            self.logger.info(f"Publishing {component_name}: {source_path}")
            self.ftver.add_component_dict({component_name: source_path})

    def create_ftrack_movie(self):
        """
        Generate the movie file from the rendered comp.
        Upload the ftrack component on completion
        """
        if self.ftver.has_playable_component:
            self.logger.info("Playable component already exists")
            return

        self.logger.info("Creating FTrack movie...")

        # if a movie file component was found use it
        movie_component_path = self.data.get("movie_component_path")
        if movie_component_path:
            self.logger.info(f"Uploading movie path: {movie_component_path}")
            self.ftver.add_playable_component(movie_component_path)
            return

        if not self.playable_component:
            self.logger.info("No playable component")
            self.logger.info("Completed publish!")
            return

        # skip the movie generation
        if self.data.get("skip_movie", False):
            self.logger.info("Skipping movie generation")
            return

        seq_data = sequence_utils.get_sequence_data(self.playable_component)
        if seq_data.is_cache:
            self.logger.info("Cache sequence")
            self.logger.info("Completed publish!")
            return

        # use ffmpeg to create the mov file
        self.logger.info(f"Generating quicktime...")

        # define movie path
        temp_mov_path = self.data.get("mov_path")
        if not temp_mov_path:
            temp_mov_path = file_utils.temp_file_path("testing", "mov")
            self.data["mov_path"] = temp_mov_path

        self.logger.info("Using FFMpeg to create movie file")
        created = ffmpeg_utils.run_ffmpeg_hud_command(
            seq_data.start,
            seq_data.nuke_path,
            temp_mov_path
            )

        if not created:
            self.logger.critical(f"Failed to create movie file")
            return

        # remove the temp file
        self.logger.info(f"Uploading movie file: {temp_mov_path}")
        self.ftver.add_playable_component(temp_mov_path)

        # either keep and add as a component or delete from disk
        if self.data.get("keep_mov", True):
            self.ftver.add_component("movieFile", temp_mov_path)
        else:
            os.remove(temp_mov_path)
        self.logger.info("Completed publish!")


if __name__ == "__main__":
    pub_data = file_utils.read_json(sys.argv[1])
    FtrackPublish(pub_data)
