""" Set the frame range tool for maya """
import maya.cmds as cmds
import ccgeneral.widgets.frame_range as frame_range


class MayaFrameRangeWidget(frame_range.FrameRangeWidget):
    def __init__(self):
        super().__init__()

    def from_scene(self):
        # type: () -> (int, int)
        """
        Get the start and end frame from the scene

        Returns:
            start: First frame in the scene
            end: Last frame in the scene
        """
        start = int(cmds.playbackOptions(q=True, min=True))
        end = int(cmds.playbackOptions(q=True, max=True))
        return start, end
