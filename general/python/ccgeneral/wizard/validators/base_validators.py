""" Base class to validate a scene or asset """
from cccore.utils.cc_logging import cc_logger


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

    def __init__(self, data):
        super(BaseValidator, self).__init__()
        self.is_valid = bool()
        self.is_deadline = bool()
        self.message = str()
        self.nodes = list()
        self.logger = cc_logger()
        self.data = data

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
