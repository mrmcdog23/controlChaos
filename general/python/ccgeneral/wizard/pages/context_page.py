"""
Wizard page to select the context
of the entity to publish to
"""
import cccore.utils.ui_utils as ui_utils
from ccgeneral.wizard.pages.base_page import BasePublishPage
import ccgeneral.widgets.status_cmb as status_cmb
import ccgeneral.widgets.asset_cmb as asset_cmb
import ccgeneral.widgets.shot_combobox as shot_cmb


class ContextPage(BasePublishPage):
    title = "Asset context Page"
    subtitle = "Select the asset to publish to"

    def __init__(self, parent=None):
        super(ContextPage, self).__init__(parent)
        self.ftver = None
        self.cmb_status = None

    def initializePage(self):
        """
        Initialize the data of the asset types
        and names and connect the signals
        """
        super(ContextPage, self).initializePage()
        self.add_status_combo()
        self.add_context_labels()
        self.connect_signals()

    @property
    def ctx(self):
        """
        The current context
        """
        return self.wizard().ctx

    def add_context_labels(self):
        """
        Add the context labels to the widget.
        Skip if already built
        """
        if self.built_layout:
            return
        form_layout = ui_utils.context_layout_form_context(self.ctx)
        self.context_layout.addLayout(form_layout)
        self.built_layout = True

    def connect_signals(self):
        """
        Connect the widgets to the signals
        """
        self.pte_comment.textChanged.connect(self.comment_changed)

    def add_status_combo(self):
        """
        Add the ftrack combo box to the page
        """
        if self.cmb_status:
            return
        version_statuses = self.wizard().ftver.version_statuses
        self.cmb_status = status_cmb.StatusCmb(version_statuses)
        self.status_layout.addWidget(self.cmb_status)

    def comment_changed(self):
        """
        When the description is changed trigger is complete
        """
        self.completeChanged.emit()

    def isComplete(self):
        # type: () -> bool
        """
        Check there is some text in the description

        Returns:
            Whether there is text in the description
        """
        return bool(self.pte_comment.toPlainText())

    def nextId(self):
        """
        Will go to the next page
        """
        return self.wizard().FINAL_PAGE

    def skipPage(self):
        """
        Skip page if publish has been set to False
        """
        publish = self.data.get("publish", True)
        return not publish

    def validatePage(self):
        """
        Store the selected options in the wizard data
        """
        if self.ctx.is_build:
            self.data['entity'] = "build"
            self.data['asset_build_type_name'] = self.ctx.build_type
            self.data['asset_build_name'] = self.ctx.asset_build
        else:
            self.data['entity'] = "shot"
            self.data['sequence_name'] = self.ctx.sequence
            self.data['shot_name'] = self.ctx.shot
            if self.ctx.episode:
                self.data['episode_name'] = self.ctx.episode

        self.data['task_name'] = self.ctx.task
        self.data['comment'] = self.pte_comment.toPlainText()
        self.data["status_name"] = self.cmb_status.currentText()
        return True


class AssetContextPage(ContextPage):
    title = "Asset context Page"
    subtitle = "Select the asset to publish to"

    def __init__(self, parent=None):
        super(AssetContextPage, self).__init__(parent)


class ShotContextPage(ContextPage):
    title = "Shot Context Page"
    subtitle = "Select the shot to publish to"

    def __init__(self, parent=None):
        super(ShotContextPage, self).__init__(parent)


class AssetCmbContextPage(ContextPage):
    title = "Select Asset Context Page"
    subtitle = "Select the asset to publish to"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cmb_asset = None

    def add_context_labels(self):
        """
        Add the context labels to the widget.
        Skip if already built
        """
        if self.cmb_asset:
            return
        self.cmb_asset = asset_cmb.AssetCmb(
            ftasset=self.wizard().ftasset, hide_cat=False)
        self.context_layout.addWidget(self.cmb_asset)

    def validatePage(self):
        """
        Store the selected options in the wizard data
        """
        self.data.update(self.cmb_asset.get_data())
        self.data['comment'] = self.pte_comment.toPlainText()
        self.data["status_name"] = self.cmb_status.currentText()
        return True


class ShotComboBoxContextPage(ContextPage):
    title = "Select Shot Context Page"
    subtitle = "Select the shot to publish to"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cmb_shot = None

    def add_context_labels(self):
        """
        Add the context labels to the widget.
        Skip if already built
        """
        if self.cmb_shot:
            return
        self.cmb_shot = shot_cmb.ShotComboBox(
            ftshot=self.wizard().ftshot, hide_versions=True)
        self.context_layout.addWidget(self.cmb_shot)

    def validatePage(self):
        """
        Store the selected options in the wizard data
        """
        self.data.update(self.cmb_shot.get_data())
        self.data['comment'] = self.pte_comment.toPlainText()
        self.data["status_name"] = self.cmb_status.currentText()
        return True
