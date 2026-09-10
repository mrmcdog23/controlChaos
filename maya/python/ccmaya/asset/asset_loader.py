""" Asset loader for maya """
import maya.cmds as cmds
import ccmaya.utils.maya_utils as maya_utils
import ccgeneral.asset.asset_loader as asset_loader
from CCPySide import QtWidgets


class MayaAssetLoader(asset_loader.AssetLoaderBase):
    title = "Maya Load Asset"
    use_cc_ss = False

    def __init__(self, parent=None):
        self.rbn_reference = None
        self.rbn_import = None
        super().__init__(parent=parent)
        maya_utils.load_plugins(["AbcImport"])
        self.update_button_text(True)

    def add_load_options(self):
        """
        Build load option widgets
        """
        self.rbn_reference = QtWidgets.QRadioButton("Reference")
        self.rbn_reference.setChecked(True)
        self.rbn_reference.toggled.connect(self.update_button_text)
        self.rbn_import = QtWidgets.QRadioButton("Import")

        # add the radio buttons to the layout
        self.lyt_options.addItem(self.create_spacer())
        self.lyt_options.addWidget(self.rbn_reference)
        self.lyt_options.addWidget(self.rbn_import)
        self.lyt_options.addItem(self.create_spacer())

    def update_button_text(self, ref_checked):
        # type: (bool) -> None
        """
        Update the button text based on the checkbox

        Args:
            ref_checked: Is the reference radio button checked
        """
        text = "Reference" if ref_checked else "Import"
        self.btn_load_asset.setText(f"{text} Asset")

    @staticmethod
    def filtered_component_paths(component_paths):
        # type: (dict) -> dict
        """
        Filter the paths down to the ones to display
        """
        maya_files_dict = dict()
        for component_name, component_path in component_paths.items():
            if component_path.endswith(".ma"):
                maya_files_dict[component_name] = component_path

        if maya_files_dict:
            return maya_files_dict
        return component_paths

    def load_selected_version(self):
        """
        Load the alembic asset
        """
        self.save_ui_settings(self.ui_settings)
        asset_version = self.selected_version()
        self.ftver.asset_version_id = asset_version['id']

        for component_path in self.selected_components:
            if component_path.endswith((".abc", ".ma", ".fbx")):
                if self.rbn_reference.isChecked():
                    cmds.file(component_path,
                              namespace=self.ftver.asset_build_name,
                              reference=True
                              )
                else:
                    cmds.file(component_path, i=True)


def main():
    """
    Launch the maya asset loader
    """
    maya_utils.launch_maya_win(MayaAssetLoader)
