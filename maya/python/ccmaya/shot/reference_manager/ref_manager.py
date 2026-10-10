import maya.cmds as cmds
import ccftrack.asset_version as asset_version
import ccftrack.shot as shot
import cccore.base_ui as baseui
import cccore.utils.cc_logging as cc_logging
import ccmaya.utils.maya_utils as maya_utils
import ccmaya.asset.scene_asset as scene_asset
from CCPySide import QtWidgets, QtCore


# class variables
SELECTED_COLOUR = "rgb(50, 50, 250)"
DESELECTED_COLOUR = "rgb(93, 93, 93);"
FRAME_STYLE = "background-color: {0};"


class ReferenceAsset(baseui.WidgetBase):
    """
    Widget of the individual reference asset
    """
    ui_name = "reference_asset"

    def __init__(self, parent, namespace, scene_asset):
        # type: (QtWidgets.QWidget, str, scene_asset) -> None
        """
        Args:
            parent: The reference manager widget
            namespace: The asset namespace
            scene_asset: Maya scene asset
        """
        super().__init__(parent, scene_asset)
        self.is_selected = False
        self.menu = None
        self.num_to_version = None
        self.pw = parent
        self.scene_asset = scene_asset
        self.namespace = namespace

        self.setMaximumHeight(80)
        self.txt_namespace.setText(namespace)
        self.ftver = scene_asset.ftver
        self.set_ui_data()
        self.populate_versions()
        self.set_version_icon()
        self.set_loaded_state()
        self.connect_signals()

    def set_loaded_state(self):
        """
        Set the load state of the frame if not loaded
        """
        self.frame.setEnabled(self.scene_asset.is_loaded)

    def connect_signals(self):
        """
        Connect the widgets to the signal
        """
        self.cmb_version.currentIndexChanged.connect(self.update_reference)

    def set_list_mode_widget(self):
        """
        Set the widget in the list mode
        """
        self.set_widget_mode(True, 60, 20)

    def set_icon_mode_widget(self):
        """
        Set the icon mode of the widget
        """
        self.set_widget_mode(False, 80, 28)

    def set_widget_mode(self, is_hidden, height, icon_size):
        # type: (bool, int, int) -> None
        """
        Set the widget mode either list or icon

        Args:
            is_hidden: Whether to hide the thumbnail
            height: Height of the widget
            icon_size: Square size of the icon
        """
        self.thumbnail.setHidden(is_hidden)
        self.setMaximumHeight(height)
        self.lbl_type_icon.setMinimumSize(icon_size, icon_size)
        self.lbl_type_icon.setMaximumSize(icon_size, icon_size)

    def set_ui_data(self):
        """
        Set the ui information and its icons based on the ftrack Id
        """
        build_name = self.ftver.asset_build_name
        self.txt_asset_build_name.setText(build_name)
        self.set_thumbnail_image(self.ftver.thumbnail_url)
        type_name = self.ftver.asset_build_type_name
        self.set_widget_icons(icon_dict={type_name: "lbl_type_icon"})

    def populate_versions(self):
        """
        Populate the combo box versions and set to the current one
        """
        self.num_to_version = self.ftver.num_to_version
        self.cmb_version.addItems(self.num_to_version.keys())
        self.set_combobox_index(self.cmb_version, self.ftver.version_text)

    def set_version_icon(self):
        """
        Set the version icon based on if the latest
        """
        if self.ftver.is_latest:
            icon_name = "green"
        elif not self.ftver.is_valid:
            icon_name = "red"
        else:
            icon_name = "amber"
        self.set_widget_icons(icon_dict = {"version_status_icon": icon_name})

    def set_selected(self):
        """
        Set the widget selected and change the style sheet
        """
        style = FRAME_STYLE.format(SELECTED_COLOUR)
        self.frame.setStyleSheet(style)
        self.is_selected = True
        if self.scene_asset.node:
            cmds.select(self.scene_asset.node)

    def set_deselected(self):
        """
        Deselect the widget and set the de-select stylesheet
        """
        style = FRAME_STYLE.format(DESELECTED_COLOUR)
        self.frame.setStyleSheet(style)
        self.is_selected = False

    def mousePressEvent(self, event):
        """
        When an item is clicked deleted all and set the new only selected
        """
        modifiers = QtWidgets.QApplication.queryKeyboardModifiers()
        if modifiers != QtCore.Qt.ShiftModifier:
            self.pw.deselect_all()
        self.set_selected()

    def update_reference(self):
        """
        When the version is changed update the
        reference to the selected version
        """
        selected_version = self.cmb_version.currentText()
        new_version = self.num_to_version[selected_version]
        self.scene_asset.update_to_version(new_version)
        self.set_version_icon()
        self.pw.set_update_all_button()

    def remove_reference_and_shader(self):
        """
        Remove the selected asset
        """
        self.scene_asset.remove_reference()

    def load_unload_reference(self):
        """
        Do the opposite of the load of the reference
        """
        try:
            self.scene_asset.toggle_load()
        except:
            pass
        self.set_loaded_state()

    @property
    def is_latest_version(self):
        # type: () -> bool
        """
        If the current version is the latest.
        True if the reference is up-to-date
        """
        return bool(self.cmb_version.currentIndex() == 0)


class ReferenceManager(baseui.WindowBase):
    """
    The reference manager window for managing references
    """
    title = "Reference Manager"
    widget_to_icon = {
        "lbl_ritzy_icon": "ritzy_large",
        "btn_list_view": "list_view",
        "btn_icon_view": "icon_view",
        "btn_refresh": "refresh"
    }

    def __init__(self, parent=None):
        # type: (baseui.WindowBase) -> None
        """
        Args:
            parent: The maya session
        """
        super().__init__(parent)
        self.apply_style_sheet_to_widgets([self.btn_close_ui])
        self.btn_close_ui.clicked.connect(self.close)

        # set class variables
        self.logger = cc_logging.cc_logger()
        self.asset_widgets = list()
        self.ftver = asset_version.FtAssetVersion()
        self.ftshot = shot.FtShot(session=self.ftver.session)

        # run the setup functions
        self.populate_references()
        self.connect_signals()

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.btn_update_all_to_latest.clicked.connect(self.update_all_to_latest)
        self.btn_remove_checked_assets.clicked.connect(self.remove_checked_assets)
        self.btn_list_view.toggled.connect(self.switch_mode)
        self.btn_load_selected.clicked.connect(self.toggle_load_state)

    @property
    def selected_widget(self):
        # type: () -> list[ReferenceAsset]
        """
        Get the selected widget

        Returns:
            selected_widgets: The selected widgets reference
        """
        selected_widgets = list()
        for widget in self.asset_widgets:
            if widget.is_selected:
                selected_widgets.append(widget)
        return selected_widgets

    def reassign_shaders(self):
        """
        Reassign all shader to the reference
        """
        for widget in self.selected_widget:
            widget.reassign()
        self.deselect_all()

    def toggle_load_state(self):
        """
        Load or unload the reference
        """
        for widget in self.selected_widget:
            widget.load_unload_reference()
        self.deselect_all()

    def set_opposite_checked(self):
        """
        Set the opposite tool button as checked
        """
        is_checked = self.btn_list_view.isChecked()
        if is_checked:
            self.btn_icon_view.setChecked(False)

    def switch_mode(self):
        """
        Switch the view mode of the widgets
        """
        self.set_opposite_checked()
        list_mode = self.btn_list_view.isChecked()
        for asset_widget in self.asset_widgets:
            if list_mode:
                asset_widget.set_list_mode_widget()
            else:
                asset_widget.set_icon_mode_widget()

    def remove_checked_assets(self):
        """
        Remove the selected reference
        """
        checked_assets = self.get_checked_assets()
        if not checked_assets:
            maya_utils.maya_messagebox("Nothing Selected",
                                       "No assets selected",
                                       "critical"
                                       )
            return
        remove_asset = maya_utils.maya_messagebox(
            "Remove",
            f"Remove {len(checked_assets)} assets(s)?",
            "question",
            ["Remove", "Cancel"]
        )

        if remove_asset == 1:
            return
        for checked_asset in checked_assets:
            checked_asset.remove_reference_and_shader()
            checked_asset.setHidden(True)

    def refresh(self):
        """
        Delete current widgets and repopulate
        """
        for asset_widget in self.asset_widgets:
            asset_widget.deleteLater()
        self.asset_widgets = list()
        self.populate_references()

    def update_all_to_latest(self):
        """
        Set all the combo boxes to the latest
        """
        for asset_widget in self.asset_widgets:
            asset_widget.cmb_version.setCurrentIndex(0)

    def get_checked_assets(self):
        # type: () -> list[ReferenceAsset]
        """
        Get the selected reference name

        Returns:
            asset_widget: Selected widget
        """
        checked_assets = list()
        for asset_widget in self.asset_widgets:
            if asset_widget.is_selected:
                checked_assets.append(asset_widget)
        return checked_assets

    def populate_references(self):
        """
        Using pymel get all assets with ftrack id
        attribute and build a widget from it
        """
        self.logger.info("Populate references...")
        shot_assets_dict = maya_utils.get_scene_assets(session=self.ftver.session)
        for namespace, scene_asset_to_find in shot_assets_dict.items():
            asset_widget = ReferenceAsset(self, namespace, scene_asset_to_find)
            self.vert_layout.addWidget(asset_widget)
            self.asset_widgets.append(asset_widget)
        self.set_update_all_button()

        # account for unloaded references
        for ref_node in cmds.ls(type="reference"):
            try:
                is_loaded = cmds.referenceQuery(ref_node, isLoaded=True)
                if is_loaded:
                    continue
            except RuntimeError:
                continue

            # Namespace the node lives in
            ns = cmds.referenceQuery(ref_node, namespace=True)
            namespace = ns.replace(":", "")
            asset = scene_asset.SceneAsset(
                namespace=namespace, ref_node=ref_node, session=self.ftver.session)
            asset_widget = ReferenceAsset(self, ref_node, asset)
            self.vert_layout.addWidget(asset_widget)
            self.asset_widgets.append(asset_widget)

    def deselect_all(self):
        """
        Deselect all asset widgets
        """
        for asset_widget in self.asset_widgets:
            asset_widget.set_deselected()

    def set_update_all_button(self):
        """
        Enable the update all button if not
        all references are up-to-date
        """
        all_up_to_date = False
        for asset_widget in self.asset_widgets:
            if not asset_widget.is_latest_version:
                all_up_to_date = True
                break
        self.btn_update_all_to_latest.setEnabled(all_up_to_date)


def main():
    """ Launch the reference manager """
    maya_utils.launch_maya_win(ReferenceManager)
