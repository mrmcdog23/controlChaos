""" Houdini publish validation page """
from ccgeneral.wizard.validators.base_validators import BaseValidator
import cchoudini.wizard.validators.shared_validators as shared_validators
import cchoudini.wizard.validators.shot_validators as shot_validators
from ccgeneral.wizard.pages.validate_page import ValidatePage


class HouValidatePage(ValidatePage):
    def __init__(self, parent=None):
        super(HouValidatePage, self).__init__(parent)

    @property
    def shared_validators(self):
        # type: () -> shared_validators
        """ File of the shared validators """
        return shared_validators

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
        type such as matching node type

        Args:
            valid_cls: The class of the validator
            data: Data of te publish

        Returns:
            True if valid
        """
        used_on_node_types = valid_cls.node_types
        if used_on_node_types and data["node_type"] not in used_on_node_types:
            return False
        return True

