"""
Maya publish validation page
"""
import ccmaya.wizard.validators.asset_validators as asset_validators
import ccmaya.wizard.validators.shot_validators as shot_validators
import ccmaya.wizard.validators.shared_validators as shared_validators
from ccgeneral.wizard.pages.validate_page import ValidatePage
from ccgeneral.wizard.validators.base_validators import BaseValidator


class MayaValidatePage(ValidatePage):
    def __init__(self, parent=None):
        super(MayaValidatePage, self).__init__(parent)

    @property
    def shared_validators(self):
        # type: () -> shared_validators
        """ File of the shared validators """
        return shared_validators

    @property
    def asset_validators(self):
        # type: () -> asset_validators
        """ File of the asset validators """
        return asset_validators

    @property
    def shot_validators(self):
        # type: () -> shot_validators
        """ File of the shot validators """
        return shot_validators

    @staticmethod
    def is_registered(valid_cls, data):
        # type: (BaseValidator, dict) -> bool
        """
        Whether the validate class is of the published
        type such as matching task name in this case

        Args:
            valid_cls:  The class of the validator
            data: Data of te publish

        Returns:
            True if valid
        """
        if valid_cls.task_names and data["task_name"] not in valid_cls.task_names:
            return False

        # check if the asset type is to be ignored
        asset_type = data.get("asset_build_type_name", "none")
        if asset_type in valid_cls.ignore_types:
            return False
        return True
