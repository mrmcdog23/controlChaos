
""" ftrack publish file to create asset versions """
import sys
import maya.cmds as cmds
import ccftrack.asset_version as asset_version
import ccftrack.shot as shot
import ccftrack.asset as asset
import cccore.utils.file_utils as file_utils
import cccore.utils.cc_logging as cc_logging
import cccore.data.server_data as server_data
import ccmaya.render.create_playblast as create_playblast

# initialize maya standalone
try:
    import maya.standalone
    maya.standalone.initialize()
except (TypeError, RuntimeError):
    pass


class PlayblastBatch(object):
    """
    Publish an asset or sequence to ftrack
    """
    def __init__(self, data, start_frame, end_frame):
        # type: (dict, int, int) -> None
        """
        Args:
            data: Publish information dictionary
            start_frame: First frame to playblast
            end_frame: Last frame to playblast
        """
        self.data = data
        self.start_frame = start_frame
        self.end_frame = end_frame

        self.logger = cc_logging.cc_logger()
        self.ftver = asset_version.FtAssetVersion()
        self.ftshot = shot.FtShot(session=self.ftver.session)
        self.ftasset = asset.FtAsset(session=self.ftver.session)
        self.project_data = server_data.ProjectData()
        self.logger.info(f"data: {self.data}")
        self.logger.info(f"Start: {self.start_frame}   End: {self.end_frame}")

        cmds.file(self.data['wip_file_path'],  open=True, force=True)

        # generate scene playblast
        render_data = self.data.copy()
        render_data["start"] = self.start_frame
        render_data["end"] = self.end_frame
        render_data["name"] = self.data["shot_name"]

        self.logger.info(f"Rendering shot: {render_data}")
        pb_inst = create_playblast.PlayblastScene(render_data)
        pb_inst.set_render_globals()
        pb_inst.render_scene()


if __name__ == "__main__":
    pb_data = file_utils.read_json(sys.argv[1])
    start = int(sys.argv[2])
    end = int(sys.argv[3])
    PlayblastBatch(pb_data, start, end)
