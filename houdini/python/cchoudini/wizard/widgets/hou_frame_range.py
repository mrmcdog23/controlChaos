""" Interface to set the frame range """
import hou
import ccgeneral.widgets.frame_range as frame_range


NODE_RANGE = "Node Range"
SCENE_RANGE = frame_range.SCENE_RANGE
FTRACK_RANGE = frame_range.FTRACK_RANGE
CUSTOM_RANGE = frame_range.CUSTOM_RANGE


class HouFrameRangeWidget(frame_range.FrameRangeWidget):
    FRAME_RANGE_OPTIONS = [NODE_RANGE,
                           SCENE_RANGE,
                           FTRACK_RANGE,
                           CUSTOM_RANGE
                           ]

    def __init__(self):
        """
        The frame range widget
        """
        super(HouFrameRangeWidget, self).__init__()

    def from_scene(self):
        current_start, current_end = hou.playbar.frameRange()
        return int(current_start), int(current_end)
