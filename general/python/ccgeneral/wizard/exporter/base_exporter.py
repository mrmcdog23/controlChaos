""" Base exporter to be subclassed with exporters """
import os
import logging
import cccore.core_constants as core_constants
import cccore.utils.file_utils as file_utils
import ccftrack.asset_version as ft_version
import ccftrack.asset as asset
import ccftrack.shot as shot
import ccftrack.query as query
import ccftrack.publish as publish


class BaseExporter(object):
    """
    Base exporter for running wizard tasks
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._progress = 0
        self.ui = None
        self.data = None
        self.ctx = None
        self.start_frame = int()
        self.end_frame = int()
        self.namespace_to_data = dict()
        self.exported_files_to_data = dict()
        self.additional_components = dict()
        self.asset_version = None
        self.ftver = ft_version.FtAssetVersion()
        self.ftasset = asset.FtAsset(session=self.ftver.session)
        self.ftshot = shot.FtShot(session=self.ftver.session)
        self.ftquery = query.FtQuery(session=self.ftver.session)

    @property
    def master_scene(self):
        pass

    def add_to_percentage(percentage):
        """
        Decorator to add a percentage to the progress

        Args:
            percentage: Amount to add to the progress
        """
        def decorator(func):
            """ Decorator for the progress """
            def wrapper(self, *args, **kwargs):
                self.add_progress(percentage)
                return func(self, *args, **kwargs)
            return wrapper
        return decorator

    def open_file(self):
        """ Open the file to work on """
        pass

    def pre_export(self):
        """ Tasks to run before the export begins """
        pass

    def post_export(self):
        """ Tasks to run after the export begins """
        pass

    def export(self):
        """ Main functions to run to export """
        pass

    def add_progress(self, increment):
        # type: (int) -> None
        """
        Add progress to the progress page. If the ui is set add
        directly to the progress bar. If not send the text and
        that will use the grep to extract the progress value

        Args:
            increment: Value to add to the progress page
        """
        if self.ui:
            self.ui.progress_wdg.add_to_progress(increment)
        else:
            self.logger.info(f"{core_constants.PROGRESS_TEXT} {increment}")

    def set_maximum_progress_bar(self, maximum_value):
        # type: (int) -> None
        """
        Set the maximum value of the progress page

        Args:
            maximum_value: Value to add to the progress page
        """
        if self.ui:
            self.ui.progress_wdg.set_maximum_progress(maximum_value)
        else:
            self.logger.info(f"{core_constants.MAXIMUM_VALUE_TEXT} {maximum_value}")

    def complete_exporter_progress(self):
        """
        Set the exporter progress to 100%
        """
        self.ui.progress_wdg.complete_progress_bar()

    def finish_exporter_process(self):
        """ Complete export process """
        self.ui.progress_wdg.process_finished()

    def log(self, message):
        # type: (str) -> None
        """
        Log message and update progress bar

        Args:
            message: Message to be logged and displayed
        """
        if self.ui:
            self.ui.add_message(message)
        else:
            self.logger.info(message)

    def batch_process(self, json_path):
        # type: (str) -> None
        """
        Run the process in batch mode

        Args:
            json_path: Json of the published data
        """
        self.log("Loaded app..")
        self.data = file_utils.read_file(json_path)

        # open the file
        self.open_file()

        # run the export
        self.export()

    def write_metadata(self):
        """
        Write the metadata json file
        """
        # update and save all metadata
        data = {
            "exported_files_to_data": self.exported_files_to_data,
            "start_frame": self.start_frame,
            "end_frame": self.end_frame,
            "master_scene": self.master_scene
        }
        data.update(self.data)

        # work out the data path to save
        self.ctx.use_suffix = "metadata"
        data_file_path = self.ctx.data_file_path
        self.logger.info(f"Writing metadata: {data_file_path}")

        file_utils.create_directories(os.path.dirname(data_file_path))
        file_utils.write_file(data_file_path, data)

        # add the data to the dictionary
        self.additional_components["metadata"] = data_file_path

    @add_to_percentage(10)
    def publish_shot(self):
        """
        Publish the shot to ftrack
        """
        self.data["additional_components"] = self.additional_components
        publish_inst = publish.FtrackPublish(self.data)
        self.asset_version = publish_inst.asset_version
        asset_version_id = self.asset_version["id"]
        self.ftver.asset_version_id = asset_version_id
        self.log(f"Asset Version: {asset_version_id}")
