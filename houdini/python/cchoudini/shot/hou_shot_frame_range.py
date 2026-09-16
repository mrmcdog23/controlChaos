""" Set the frame range of the houdini file from ftrack """
import hou
import cchoudini.utils.hou_utils as hou_utils
import cccore.file_env.context as context
import ccgeneral.shot.frame_range.shot_frame_range as shot_frame_range


class HouShotFrameRange(shot_frame_range.ShotFrameRange):
    def __init__(self, parent=None):
        """
        Set the scene range or set it on ftrack
        """
        super(HouShotFrameRange, self).__init__(parent)

    @staticmethod
    def range_question(message):
        # type: (str) -> str
        """
        Question whether to set the frame range

        Args:
            message: Whether to process with the setting

        Returns:
            response: The response to setting
        """
        buttons = ["Set Range", "Cancel"]
        response = hou_utils.hou_messagebox("Set Range",
                                            message,
                                            "question",
                                            buttons=buttons
                                            )
        return response

    def set_new_range_from_scene(self):
        """
        Set the ui spin boxes from the scene
        """
        current_start, current_end = hou.playbar.frameRange()
        self.sb_new_start.setValue(current_start)
        self.sb_new_end.setValue(current_end)

    def set_playback_range(self, new_start, new_end):
        # type: (int, int) -> None
        """
        Set the houdini playback frame range

        Args:
            new_start: New start frame
            new_end: New end frame
        """
        hou.playbar.setFrameRange(new_start, new_end)
        self.sb_new_start.setValue(new_start)
        self.sb_new_end.setValue(new_end)
        

def main():
    """
    Launch the frame range setter in houdini
    """
    if not context.Context().shot:
        hou_utils.hou_messagebox("Not Set", "Shot is not set", "critical")
        return
    hou_utils.launch_hou_win(HouShotFrameRange)

