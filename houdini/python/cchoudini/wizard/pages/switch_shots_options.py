""" Switch shots options wizard page """
import hou
from ccgeneral.wizard.pages.base_page import BasePublishPage
from ccgeneral.widgets.tree_widget import No8TreeWidget


class SwitchShotOptionsPage(BasePublishPage):
    title = "Publish Renders"
    subtitle = "Publish the Arnold Renders on completion"

    def __init__(self, parent=None):
        super(SwitchShotOptionsPage, self).__init__(parent)
        self.tw_shots_to_render = None
        self.create_layout()

    def initializePage(self):
        """
        Populate the page data
        """
        self.populate_data()

    def create_layout(self):
        """
        Create the layout of the ui
        """
        self.tw_shots_to_render = No8TreeWidget(["Check Shot Names to Render"])
        self.lyt_render_shots.addWidget(self.tw_shots_to_render)

    def populate_data(self):
        """
        Populate the shots list and tasks
        """
        full_shot_list = self.data["publish_shots_list"]
        self.tw_shots_to_render.populate_items(full_shot_list)
        self.cmb_task_name.clear()
        self.cmb_task_name.addItems(["animation", "lighting", "fx"])

    def validatePage(self):
        """
        Store the selected options in the wizard data
        """
        self.data['comment'] = "Automated build shot"
        self.data["status_name"] = "WIP"
        self.data["save_task_name"] = self.cmb_task_name.currentText()
        self.data["render_shots"] = self.tw_shots_to_render.items_text()
        return True
