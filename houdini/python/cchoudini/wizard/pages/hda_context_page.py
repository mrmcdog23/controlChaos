""" select the context for the hda """
import os
import hou
from typing import Optional
from CCPySide import QtWidgets
import cccore.file_env.context as context
import ccftrack.asset as asset
import cccore.core_constants as core_constants
import cchoudini.wizard.widgets.hda_cmb as hda_cmb
from ccgeneral.wizard.pages.context_page import ContextPage
from ccgeneral.wizard.pages.base_page import BasePublishPage


class HDAProjectContextPage(ContextPage):
    title = "Houdini Digital Asset context Page"
    subtitle = "Select the HDA to publish to"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hda_wdg = None

    def add_context_labels(self):
        """
        Add the asset labels widget
        """
        if self.built_layout:
            return
        self.hda_wdg = hda_cmb.HDAWidget()
        self.context_layout.addWidget(self.hda_wdg)
        self.built_layout = True

    def initializePage(self):
        """
        Set button layout
        """
        super().initializePage()
        self.hda_wdg.txt_asset_type.setText(self.data['asset_build_type_name'])
        self.hda_wdg.txt_asset_name.setText(self.data['asset_build_name'])

    def validatePage(self):
        """
        Store the selected options in the wizard data
        """
        self.data['suffix'] = self.hda_wdg.cmb_suffix.currentText()
        self.data['comment'] = self.pte_comment.toPlainText()
        self.data["status_name"] = self.cmb_status.currentText()
        return True

    def skipPage(self):
        # type: () -> bool
        """
        If it's a not a project publish skip the page
        """
        return self.data.get('library')


class HDALibraryContextPage(ContextPage):
    title = "Houdini Digital Library context Page"
    subtitle = "Input name of the HDA to publish"
    LIB_TASK = "fx"
    LIB_ASSET_TYPE = "otls"
    CORE_HDA_NAMES = ["cccache", "ccwedger", "ccsubmit"]

    def __init__(self, parent=None):
        super(HDALibraryContextPage, self).__init__(parent)
        self.cmb_hda_name = None

    def add_context_labels(self):
        """
        Add the asset labels widget
        """
        if self.built_layout:
            return
        form_layout = QtWidgets.QFormLayout()
        lbl_hda_name = QtWidgets.QLabel("HDA Name: ")
        self.cmb_hda_name = QtWidgets.QComboBox()
        form_layout.addRow(lbl_hda_name, self.cmb_hda_name)
        self.context_layout.addLayout(form_layout)
        self.built_layout = True

    def initializePage(self):
        """
        Set button layout
        """
        super().initializePage()

        # add library hda names
        ftasset_lib = asset.FtAsset(input_project=core_constants.LIBRARY)
        lib_hda_names = ftasset_lib.get_asset_build_names(asset_type="hda")

        # filter out core hda's
        filtered_lib_hda_names = list()
        for hda_name in lib_hda_names:
            if hda_name not in self.CORE_HDA_NAMES:
                filtered_lib_hda_names.append(hda_name)

        self.cmb_hda_name.clear()
        self.cmb_hda_name.setFixedWidth(150)
        self.cmb_hda_name.setEditable(True)
        self.cmb_hda_name.addItems(lib_hda_names)
        self.create_completer(self.cmb_hda_name,
                              items_list=lib_hda_names
                              )

    def validatePage(self):
        """
        Store the selected options in the wizard data
        """
        self.data["asset_build_type_name"] = self.LIB_ASSET_TYPE
        self.data["task_name"] = self.LIB_TASK
        self.data['asset_build_name'] = self.cmb_hda_name.currentText()
        self.data['comment'] = self.pte_comment.toPlainText()
        self.data["status_name"] = self.cmb_status.currentText()
        return True

    def skipPage(self):
        # type: () -> bool
        """
        If it's a not a library publish skip the page
        """
        return not self.data.get('library')


class HDAShowOrGeneralPage(BasePublishPage):
    title = "Project or library"
    subtitle = "Is the HDA for the project or can be reused"

    def __init__(self, parent=None):
        super(HDAShowOrGeneralPage, self).__init__(parent)
        self.rbn_project = None
        self.rbn_library = None
        self.lbl_status = None
        self.is_valid = False
        self.publish_node = None
        self.create_layout()
        self.connect_signals()

    def create_layout(self):
        """
        Create the options to save as a project HDA or general
        """
        # add radio buttons
        self.rbn_project = QtWidgets.QRadioButton("Project")
        self.rbn_library = QtWidgets.QRadioButton("Library")
        self.rbn_project.setChecked(True)
        self.main_layout.addWidget(self.rbn_project)
        self.main_layout.addWidget(self.rbn_library)

        # add status label
        self.lbl_status = QtWidgets.QLabel("Is Valid")
        self.main_layout.addWidget(self.lbl_status)

    def connect_signals(self):
        """
        Connect signals to the widgets
        """
        self.rbn_project.toggled.connect(self.update_status)

    def initializePage(self):
        super().initializePage()
        node_path = self.data.get("node_path")
        self.publish_node = hou.node(node_path)
        self.update_status(True)

    @property
    def ftrack_id(self):
        # type: () -> Optional[str]
        """ The ftrack id parameter if it exists"""
        if not self.publish_node:
            return None
        ftrack_id_parm = self.publish_node.parm("ftrack_id")
        if not ftrack_id_parm:
            return None
        return ftrack_id_parm.eval()

    def update_status(self, project):
        # type: (bool) -> None
        """
        Update the status text

        Args:
            project: True if project is checked
        """
        if not project:
            self.lbl_status.setHidden(True)
            self.is_valid = True
        else:
            if self.ftrack_id:
                self.lbl_status.setHidden(True)
                self.is_valid = True

            elif not context.Context().asset_build:
                self.lbl_status.setText("Asset context is not set")
                self.lbl_status.setHidden(False)
                self.is_valid = False

            elif context.Context().asset_build:
                self.lbl_status.setHidden(True)
                self.is_valid = True

        self.completeChanged.emit()

    def validatePage(self):
        """
        Store the selected options in the wizard data
        """
        self.data['library'] = self.rbn_library.isChecked()

        if self.ftrack_id:
            ftver = self.wizard().ftver
            ftver.asset_version_id = self.ftrack_id
            self.data['asset_build_type_name'] = ftver.asset_build_type_name
            self.data['asset_build_name'] = ftver.asset_build_name
            self.data['task_name'] = ftver.task_name
        else:
            ctx = context.Context()
            self.data['asset_build_type_name'] = ctx.build_type
            self.data['asset_build_name'] = ctx.asset_build
            self.data['task_name'] = ctx.task
        return True

    def isComplete(self):
        """
        Determine whether the Next or Finish
        button should be enabled or disabled.
        """
        return self.is_valid
