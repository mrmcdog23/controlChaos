""" Base class to validate a scene or asset """
import cccore.utils.cc_logging as cc_logging
import cccore.file_env.context as context
import ccftrack.shot as shot
import ccftrack.asset as asset


class BaseValidator(object):
    """
    Base validator for analysing scenes and assets
    """
    validator_type = str()
    is_autofixable = bool()
    task_names = list()
    ignore_types = list()
    node_types = list()
    deadline_validator = bool()

    def __init__(self, session, data):
        super(BaseValidator, self).__init__()
        self.is_valid = bool()
        self.is_deadline = bool()
        self.message = str()
        self.nodes = list()
        self.logger = cc_logging.cc_logger()
        self.data = data
        self.session = session
        self.ftasset = asset.FtAsset(session=session)
        self.ftshot = shot.FtShot(session=self.ftasset.session)

    @property
    def validate(self):
        """
        Run a validation on the asset
        """
        raise NotImplemented

    def fix(self):
        """
        Run fix on the asset
        """
        raise NotImplemented


class BaseFtrackRangeValidator(BaseValidator):
    """
    Run check the frame range on ftrack matches
    """
    validator_type = "Is the FTrack range the same as the scene range"
    is_autofixable = True

    def __init__(self, session, data):
        super().__init__(session, data)
        ctx = context.Context()
        self.ftshot.set_from_context(ctx)

    def scene_frame_range(self):
        # type: () -> (int, int)
        """
        Get the frame range of the scene file
        """
        raise NotImplemented

    def validate(self):
        """
        Check the ftrack range matches the scene range
        """
        self.message = str()
        self.is_valid = True
        self.message = "Scene range matches FTrack range"
        ftrack_start = self.ftshot.start
        ftrack_end = self.ftshot.end

        # get the scene frame range
        start, end = self.scene_frame_range()

        # compare the start frame
        if start != ftrack_start:
            self.message = f"Scene start {start}. FTrack start {ftrack_start}\n"
            self.is_valid = False

        # compare the end frame
        if end != ftrack_end:
            self.message += f"Scene end {end}. FTrack end {ftrack_end}\n"
            self.is_valid = False

    def fix(self):
        """
        Update to the FTrack range to match scene
        """
        new_start, new_end = self.scene_frame_range()
        self.ftshot.set_range(new_start=new_start,
                              new_end=new_end
                              )
