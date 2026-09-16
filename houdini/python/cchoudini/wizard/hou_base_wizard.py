""" Base wizard for houdini """
import hou
import cccore.file_env.context as context
import ccgeneral.wizard.base_wizard as base_wizard


class HouBaseWizard(base_wizard.BaseWizard):
    def __init__(self, parent=hou.qt.mainWindow(), args=None):
        super(HouBaseWizard, self).__init__(parent)
        self.data["node_type"] = str()

        # find and store the houdini node in the data
        if args and args.get("node"):
            self.node = args.get("node")
            self.data["node_path"] = self.node.path()
        else:
            self.selected_nodes = hou.selectedNodes()
            if self.selected_nodes:
                self.node = self.selected_nodes[0]
                self.data["node_path"] = self.node.path()

        # apply the style sheet in houdini
        self.load_houdini_style_sheet()

    @staticmethod
    def wip_file_path():
        # type: () -> str
        """
        Get the current wip file path
        """
        return hou.hipFile.name()

    @classmethod
    def run_checks(cls):
        # type: () -> str
        """
        Run checks that are vital before opening the publishing wizard

        Returns:
            message: The error message if there is one
        """
        ctx = context.Context()
        nodes = hou.selectedNodes()

        message = None
        if cls.wip_file_path() == "untitled.hip":
            message = "File not saved"

        elif not nodes:
            message = "No node selected!"

        elif not ctx.task:
            message = "Environment not set"
        return message

