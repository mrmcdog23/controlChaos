""" Maya base wizard """
import maya.cmds as cmds
import ccgeneral.wizard.base_wizard as base_wizard
import cccore.utils.file_utils as file_utils


class MayaBaseWizard(base_wizard.BaseWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data["wip_file_path"] = self.wip_file_path()
        self.data["log_prefix"] = file_utils.get_file_name(self.wip_file_path())

    @staticmethod
    def wip_file_path():
        """ The current maya file path """
        return cmds.file(q=True, sn=True)

