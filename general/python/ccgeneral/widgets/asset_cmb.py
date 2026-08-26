""" Asset combo boxes to select the context """
from typing import Optional
import cccore.base_ui as base_ui
import cccore.file_env.context as context
import ccftrack.asset as asset


class AssetCmb(base_ui.WidgetBase):
    """
    The Ftrack combo boxes for loading assets and versions
    """
    def __init__(self,
                 ftasset=None,  # type: Optional[asset.FtAsset]
                 ctx=None,  # type: Optional[context.Context]
                 hide_ver=False,  # type: Optional[bool]
                 hide_cat=True,  # type: Optional[bool]
                 sel_tasks=False,  # type: Optional[bool]
                 hide_tasks=True  # type: Optional[bool]
                 ):
        """
        Args:
            ftasset: Ftrack asset object
            ctx: Current asset context
            hide_ver: Whether to load the version combobox
            hide_cat: Whether to hide the category option
            sel_tasks: Add an option to select the task
            hide_tasks: Hide the combobox widget for tasks
        """
        super(AssetCmb, self).__init__(ftasset=ftasset, ctx=ctx, hide_ver=hide_ver, hide_cat=hide_cat,
                                       sel_tasks=sel_tasks, hide_tasks=hide_tasks)
        self.ftasset = ftasset
        self.ctx = ctx or context.Context()
        self.hide_ver = hide_ver
        self.hide_cat = hide_cat
        self.sel_tasks = sel_tasks
        self.hide_tasks = hide_tasks

        self.populate_asset_types()
        self.populate_asset_names()
        self.populate_asset_tasks()
        self.populate_categories()
        self.connect_signals()
        self.set_versions()

    @property
    def asset_build_type(self):
        # type: () -> str
        """ The select asset build type """
        return self.cmb_asset_build_type.currentText()

    @property
    def asset_build_name(self):
        # type: () -> str
        """ The select asset build type """
        return self.cmb_asset_build_name.currentText()

    @property
    def task_name(self):
        # type: () -> str
        """ The select asset build type """
        return self.cmb_task.currentText()

    def set_versions(self):
        """
        Set the version combobox hidden if not specified.
        If not connect the task combobox to the signal
        """
        if self.hide_ver:
            self.lbl_version.setHidden(True)
            self.cmb_version.setHidden(True)
        else:
            self.cmb_task.currentIndexChanged.connect(self.populate_versions)

    def populate_asset_types(self):
        """
        Populate the asset types and set the current context default
        """
        asset_build_types_names = self.ftasset.asset_build_types_names
        self.cmb_asset_build_type.addItems(asset_build_types_names)
        self.add_icons_to_combo(self.cmb_asset_build_type, asset_build_types_names)
        self.set_combobox_index(self.cmb_asset_build_type, self.ctx.build_type)

    def connect_signals(self):
        """
        Connect the widgets to the signals
        """
        self.cmb_asset_build_type.currentIndexChanged.connect(self.populate_asset_names)
        self.cmb_asset_build_name.currentIndexChanged.connect(self.populate_asset_tasks)
        self.cmb_task.currentIndexChanged.connect(self.populate_categories)

    def populate_asset_names(self):
        """
        From the selected asset type populate the names
        """
        asset_build_type_name = self.cmb_asset_build_type.currentText()
        self.ftasset.asset_build_type_name = asset_build_type_name
        build_names = self.ftasset.get_asset_build_names(asset_build_type_name)
        self.cmb_asset_build_name.clear()
        self.cmb_asset_build_name.addItems(build_names)
        self.set_combobox_index(self.cmb_asset_build_name, self.ctx.asset_build)

    def populate_asset_tasks(self):
        """
        From the selected asset name populate the tasks
        """
        if self.hide_tasks:
            self.cmb_task.blockSignals(True)
            self.cmb_task.setHidden(True)
            self.lbl_task.setHidden(True)
            return

        if not self.asset_build_name:
            self.cmb_task.clear()
            return

        self.ftasset.asset_build_name = self.asset_build_name
        task_names = self.ftasset.get_asset_build_task_names(self.asset_build_name)

        # if select tasks add a select option
        if self.sel_tasks:
            task_names.insert(0, "<select task>")
        self.cmb_task.clear()
        self.cmb_task.addItems(task_names)
        if self.ctx and not self.sel_tasks:
            self.set_combobox_index(self.cmb_task, self.ctx.task)

    def populate_categories(self):
        """
        Populate the categories based on the selected task
        """
        if self.hide_cat:
            self.lbl_category.setHidden(True)
            self.cmb_category.setHidden(True)
            return

        self.ftasset.task_name = self.cmb_task.currentText()
        category_names = self.ftasset.category_names
        self.cmb_category.clear()
        self.cmb_category.addItems(category_names)

    def set_ftasset(self):
        """
        Set the ftrack asset class values based
        on the combobox selections
        """
        self.ftasset.asset_build_type_name = self.asset_build_type
        self.ftasset.asset_build_name = self.asset_build_name
        self.ftasset.task_name = self.task_name
        if not self.hide_cat:
            self.ftasset.category = self.cmb_category.currentText()

    def populate_versions(self):
        """
        Populate the combobox versions
        """
        self.set_ftasset()
        for version in self.ftasset.asset_versions:
            self.cmb_asset_build_type.addItem(str(version['version']))

    def get_data(self):
        # type: () -> dict
        """
        Get the selected assets data

        Returns:
            data: The selected combobox information
        """
        data = {"entity": "build",
                "asset_build_type_name": self.asset_build_type,
                "asset_build_name": self.asset_build_name,
                "task_name": self.task_name
                }
        return data
