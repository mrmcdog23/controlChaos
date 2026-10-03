""" Import shot to Unreal """
import os
import cccore.base_ui as base_ui
import cccore.utils.file_utils as file_utils
import cccore.file_env.context as context
import cccore.utils.cc_logging as cc_logging
import ccftrack.shot as shot
import ccftrack.asset_version as ft_version
from CCPySide import QtWidgets, QtCore, QtGui
from ccgeneral.widgets.shot_combobox import ShotComboBox


class LoadShotUI(base_ui.WidgetBase):
    title = "Import Shot"
    window_icon = "shot"
    control_chaos_ss = "../../css/ue_stylesheet.css"
    ignore_types = list()
    widget_to_icon = {
        "lbl_usd": "usd",
        "lbl_fbx": "fbx",
        "lbl_alembic": "abc"
    }

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ui_settings = QtCore.QSettings('controlChaos', 'ue_load_shot')
        self.ftshot = shot.FtShot()
        self.ftver = ft_version.FtAssetVersion(session=self.ftshot.session)
        self.logger = cc_logging.cc_logger()
        self.ctx = None
        self.data = dict()
        self.all_usd = str()

        self.load_settings()
        self.create_layout()
        self.populate_files()
        self.connect_signals()

    def create_layout(self):
        """
        Create the layout for the ui
        """
        self.cmb_shot = ShotComboBox(self.ftshot, ctx=self.ctx, hide_versions=False)
        self.lyt_shot_combo.addWidget(self.cmb_shot)

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.btn_import_files.clicked.connect(self.import_files)
        self.cmb_shot.cmb_version.currentIndexChanged.connect(self.populate_files)
        self.rbn_all.group().buttonClicked.connect(self.filter_files)
        self.chk_all_usd.clicked.connect(self.enable_all)

    def enable_all(self, enable):
        self.lw_import_files.setEnabled(not enable)

    def filter_files(self, radio_button):
        # type: (QtWidgets.QRadioButton) -> None
        """
        Show or hide the list widget item

        Args:
            radio_button: The clicked radio button
        """
        import_type = radio_button.text().lower()
        for index in range(self.lw_import_files.count()):
            item = self.lw_import_files.item(index)
            if import_type == "all":
                hide = False
            else:
                hide = not item.text().endswith(import_type)
            item.setHidden(hide)

    def enable_btn(self):
        """
        Enable the new shot button
        """
        if self.rbn_new_shot.isChecked():
            new_name = self.le_new_shot.text()
            self.btn_import_files.setEnabled(bool(new_name))
        else:
            self.btn_import_files.setEnabled(True)

    def populate_files(self):
        """
        Update the version list based on the asset selection
        """
        self.all_usd = str()
        self.lw_import_files.clear()

        # get the versions from the combo boxes
        version_num = self.cmb_shot.cmb_version.currentText()
        if not version_num:
            return

        asset_version = self.ftshot.get_asset_version_from_number(version_num)
        self.ftver.asset_version_id = asset_version["id"]
        for component_name, component_path in self.ftver.component_to_path.items():
            file_name = os.path.basename(component_path)

            if component_name == "metadata":
                self.data = file_utils.read_file(component_path)
                continue

            if component_path.endswith(tuple(self.ignore_types)):
                continue

            if file_name.endswith(".usd") and "_all_" in file_name:
                self.all_usd = component_path
                continue

            # get the icon path
            icon_name = file_utils.get_extension(component_path)
            icon_path = self.get_icon_path(icon_name)

            # create list widget item
            item = QtWidgets.QListWidgetItem(file_name)
            item.setCheckState(QtCore.Qt.Checked)
            item.setData(QtCore.Qt.UserRole, component_path)
            item.setIcon(QtGui.QIcon(icon_path))
            self.lw_import_files.addItem(item)

        # set the frame range from the data
        self.sb_start_frame.setValue(self.ftshot.start)
        self.sb_end_frame.setValue(self.ftshot.end)

        # set the ftrack widgets
        self.txt_created_by.setText(self.ftver.created_by)
        self.txt_comments_by.setText(self.ftver.comment)

        # hide or show the usd checkobox and enable options
        usd_all_file_found = bool(self.all_usd)
        self.grp_import_all.setHidden(not usd_all_file_found)
        if not usd_all_file_found:
            enable_files = True
        elif usd_all_file_found and self.chk_all_usd.isChecked():
            enable_files = False
        else:
            enable_files = True
        self.lw_import_files.setEnabled(enable_files)

    @property
    def start_frame(self):
        # type: () -> int
        """ The start frame in the ui """
        return self.sb_start_frame.value()

    @property
    def end_frame(self):
        # type: () -> int
        """ The end frame in the ui """
        return self.sb_end_frame.value()

    @property
    def import_files_list(self):
        # type: () -> list[str]
        """ Get a list of checked cameras """
        import_files = list()
        for index in range(self.lw_import_files.count()):
            item = self.lw_import_files.item(index)
            if item.checkState() != QtCore.Qt.CheckState.Checked:
                continue
            if item.isHidden():
                continue
            file_path = item.data(QtCore.Qt.UserRole)
            import_files.append(file_path)
        return import_files

    def import_files(self):
        """
        Import cameras into unreal
        """
        pass