""" Create a playblast of the scene """
import os
import glob
import tempfile
import maya.mel as mel
import maya.cmds as cmds
import mtoa.core as core
import cccore.utils.cc_logging as cc_logging
import cccore.utils.ffmpeg_utils as ffmpeg_utils
import cccore.utils.file_utils as file_utils
import cccore.utils.sequence_utils as sequence_utils
import cccore.data.server_data as server_data
import ccmaya.utils.maya_utils as maya_utils


GLOBAL_ATTR_VALUE = {
    "outFormatControl": 0,
    "animation": 1,
    "putFrameBeforeExt": 1,
    "extensionPadding": 4,
    "periodInExt": 1,
    "imageFormat": 32
}
NAME = "TEMP"
MAYA_HARDWARE = "mayaHardware2"
BATCH_RENDER_CMD = 'global string $ogsRenderOptions = "";' \
                   'mayaBatchRenderProcedure(0, "", "",' \
                   ' "{renderer}", $ogsRenderOptions);'


class PlayblastScene(object):
    def __init__(self, render_data):

        self.render_data = render_data
        self.logger = cc_logging.cc_logger()
        self.project_data = server_data.ProjectData()

        self.playblast_dir = str()
        self.bg = float()
        self.completed_renders = list()
        self.mov_path = str()
        self.created_mov = bool()

        # set data from the dictionary given
        self.height = render_data.get("height")
        self.width = render_data.get("width")
        self.name = render_data.get("name", NAME)
        self.renderer = render_data.get("renderer")

    @property
    def start_frame(self):
        min_time = int(cmds.playbackOptions(q=True, min=True))
        return self.render_data.get("start_frame", min_time)

    @property
    def end_frame(self):
        max_time = int(cmds.playbackOptions(q=True, max=True))
        return self.render_data.get("end_frame", max_time)

    @property
    def is_arnold_render(self):
        # type: () -> bool
        """ If it is an arnold render """
        return self.render_data["renderer"] == "arnold"

    def create_images(self):
        # type: () -> str
        """
        Render and generate a mov file

        Returns:
            mov_path: Path to the movie file
        """
        if self.is_arnold_render:
            self.arnold_settings()
        else:
            self.hardware_settings()
        self.set_render_globals()
        self.set_scene_render_camera()
        self.playblast_scene()
        self.get_completed_renders()
        self.convert_to_movie()

    def arnold_settings(self):
        self.logger.info(f"Setting to playblast settings...")
        self.bg = 0.0
        cmds.loadPlugin("mtoa", quiet=True)
        core.createOptions()  # makes sure defaultArnoldRenderOptions exists
        cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")
        cmds.setAttr("defaultArnoldRenderOptions.abortOnLicenseFail", 0)

    def hardware_settings(self):
        self.logger.info(f"Setting to Arnold renderer...")
        self.bg = 0.24
        mel.eval("setCurrentRenderer mayaHardware2")

    def set_render_globals(self):
        """
        Set the general render globals such
        as resolution and frame range
        """
        # set output resolution
        cmds.setAttr('defaultResolution.width', self.width)
        cmds.setAttr('defaultResolution.height', self.height)
        cmds.setAttr('defaultRenderGlobals.imageFilePrefix', self.name, type="string")

        # set frame range
        frame_ranges = {"startFrame": self.start_frame, "endFrame": self.end_frame}
        GLOBAL_ATTR_VALUE.update(frame_ranges)

        for attr, value in GLOBAL_ATTR_VALUE.items():
            attribute = f"defaultRenderGlobals.{attr}"
            self.logger.info(f"Setting... {attribute} ...to... {value}")
            cmds.setAttr(attribute, value)

        # set colour management and appdata directory
        cmds.colorManagementPrefs(e=True, outputTransformEnabled=True)
        self.playblast_dir = file_utils.join_file_names(tempfile.gettempdir(), "playblast")
        self.logger.info(f"Render directory: {self.playblast_dir}")
        file_utils.create_directory(self.playblast_dir)
        cmds.workspace(self.playblast_dir, openWorkspace=True)

    @property
    def render_camera(self):
        return maya_utils.render_cameras()[0]

    def set_scene_render_camera(self):
        """
        Set the scene render camera background
        """
        for scene_cam in cmds.ls(type="camera"):
            cmds.setAttr(f"{scene_cam}.renderable", 0)

        # set render camera
        cmds.setAttr(f"{self.render_camera}.renderable", 1)
        attr = f"{self.render_camera}.backgroundColor"
        cmds.setAttr(attr, self.bg, self.bg, self.bg, type="double3")

    def get_completed_renders(self):
        # type: () -> list[str]
        """
        Where the renders go is unpredictable so search all
        the subdirectories. If it's not in images then search
        the entire root for the renders.
        """
        regex = f"{self.playblast_dir}/images/**/{self.name}*.*"
        self.logger.info(f"Regex: {regex}")
        self.completed_renders = glob.glob(regex, recursive=True)

        if not self.completed_renders:
            regex = f"{self.playblast_dir}/**/{self.name}*.*"
            self.logger.info(f"Sub regex: {regex}")
            self.completed_renders = glob.glob(regex, recursive=True)

        # log renders found
        number_found = len(self.completed_renders)
        self.logger.info(f"Found: {number_found}")

    def playblast_scene(self):
        """
        Create the hardware render
        """
        for frame_num in range(self.start_frame, (self.end_frame + 1)):
            self.logger.info(f"Rendering frame: {frame_num}")
            cmds.currentTime(frame_num, e=True)
            cmds.setAttr("defaultRenderGlobals.startFrame", frame_num)
            cmds.setAttr("defaultRenderGlobals.endFrame", frame_num)
            render_cmd = BATCH_RENDER_CMD.format(renderer=self.renderer)
            self.logger.info(render_cmd)
            mel.eval(render_cmd)
        self.logger.info("Render Complete")

    def convert_to_movie(self):
        """
        From the rendered image sequence generate the movie file
        """
        self.logger.info("Generating movie file...")
        image_path = self.completed_renders[0].replace("\\", "/")
        self.temp_mov_path = file_utils.temp_file_path(self.name, "mov")
        seq_data = sequence_utils.get_sequence_data(image_path)
        created = ffmpeg_utils.run_ffmpeg_hud_command(
            self.start_frame,
            seq_data.nuke_path,
            self.temp_mov_path
            )
        self.logger.info(f"Created Movie: {created}")

        # remove the render
        if created:
            for render_path in self.completed_renders:
                self.logger.info(f"Removing: {render_path}")
                os.remove(render_path)
