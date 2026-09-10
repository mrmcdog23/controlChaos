""" Base loader for assets in applications """
import os
import ftrack_api
from typing import Any
import cccore.base_ui as base_ui
import cccore.utils.ui_utils as ui_utils
from CCPySide import QtWidgets, QtCore


class LoaderBase(base_ui.WindowBase):
    label_text = str()
    title = str()
    icon_to_widget = {
        "no8_logo_text": "lbl_no8_icon",
        "load": "lbl_load_icon"
    }
    SUPPORTED_EXT = list()

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent)

    def update_versions(self):
        """
        Update the list of available versions
        """
        raise NotImplemented

    def load_selected_version(self):
        """
        Load the selected asset
        """
        raise NotImplemented

    def add_load_options(self):
        """
        Build load option widgets
        """
        pass

    def create_layout(self):
        """
        Set the interface layout and look
        """
        # set the version tree columns
        self.tw_versions.setColumnWidth(0, 55)
        self.tw_versions.setColumnWidth(1, 80)
        self.apply_btn_style_sheet()
        self.add_load_options()
        self.btn_load_asset.setText(f"LOAD {self.label_text.upper()}")

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.tw_versions.itemSelectionChanged.connect(self.update_selected_version)
        self.btn_load_asset.clicked.connect(self.load_selected_version)
        self.tw_components_list.itemSelectionChanged.connect(self.enable_load_button)

    def reset_ui(self):
        """
        Reset the ui it has the value cleared and the thumbnail reset
        """
        self.set_thumbnail_image()
        self.txt_user.setText("-")
        self.txt_status.setText("-")
        self.comments_text.setText("")
        self.txt_status.setStyleSheet("")
        self.btn_load_asset.setEnabled(False)

    def populate_version_tree(self, num_to_version_dict, ftinst):
        # type: (dict, Any) -> None
        """
        Populate the versions tree

        Args:
            num_to_version_dict: Version number to the asset version
            ftinst: The ftrack class instance
        """
        for num, version in num_to_version_dict.items():
            # add the date and version number
            pub_date = version['date'].format('DD-MM-YYYY HH:mm')
            item = QtWidgets.QTreeWidgetItem([num, pub_date])

            item.setData(0, QtCore.Qt.UserRole, version)
            self.tw_versions.addTopLevelItem(item)
            if not ftinst.is_version_valid(version):
                item.setForeground(0, QtCore.Qt.red)
                item.setForeground(1, QtCore.Qt.red)

    def selected_version(self):
        # type: () -> ftrack_api.entity.asset_version
        """
        Get the ftrack version from the selected item

        Returns:
            version: Selected asset version
        """
        version = None
        item = self.tw_versions.currentItem()
        if item:
            version = item.data(0, QtCore.Qt.UserRole)
        return version

    @property
    def selected_components(self):
        # type: () -> list[str]
        """
        Get the ftrack version from the selected item

        Returns:
            component_paths: Selected component paths
        """
        component_paths = list()
        items = self.tw_components_list.selectedItems()
        for item in items:
            component_path = item.data(0, QtCore.Qt.UserRole)
            component_paths.append(component_path)
        return component_paths

    @staticmethod
    def filtered_component_paths(component_paths):
        # type: (list[str]) -> list[str]
        """
        Filter the paths down to the ones to display
        """
        return component_paths

    def update_selected_version(self):
        """
        Update the information from the selected version
        """
        asset_version = self.selected_version()
        if not asset_version:
            return

        # set status and comments
        self.txt_status.setText(asset_version["status"]["name"])
        style_sheet = ui_utils.get_status_stylesheet(asset_version["status"])
        self.txt_status.setStyleSheet(style_sheet)
        self.comments_text.setText(asset_version['comment'])

        # get username and set it on the text
        first_name = asset_version["user"]['first_name']
        last_name = asset_version["user"]['last_name']
        user_name = f"{first_name} {last_name}"
        self.txt_user.setText(user_name)

        self.ftver.asset_version_id = asset_version["id"]
        self.set_thumbnail_image(image_path=self.ftver.thumbnail_url)

        # list components
        self.tw_components_list.clear()
        ext_tuple = tuple(self.SUPPORTED_EXT)
        component_paths = self.ftver.get_component_path_dict(ext_tuple)
        filtered_paths = self.filtered_component_paths(component_paths)

        for component_path in list(filtered_paths.values()):
            component_name = os.path.basename(component_path)
            item = QtWidgets.QTreeWidgetItem([component_name])
            item.setData(0, QtCore.Qt.UserRole, component_path)
            self.tw_components_list.addTopLevelItem(item)

    def enable_load_button(self):
        """
        Enable the load button if a component is selected
        """
        selected_components = self.selected_components
        if not selected_components:
            return
        self.btn_load_asset.setEnabled(True)
