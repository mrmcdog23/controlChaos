""" The information once a wizard process is complete """
import os
from CCPySide import QtWidgets, QtGui
from ccgeneral.wizard.pages.base_page import BasePublishPage


class CompletePage(BasePublishPage):
    title = "Publish Complete"
    subtitle = "Asset published to Ftrack"

    def __init__(self, parent=None):
        super(CompletePage, self).__init__(parent)

    def build_deadline_widget(self, job_types):
        # type: (list[str]) -> None
        """
        Work out job types widget so its clear what's been submitted

        Args:
            job_types: List of job types
        """
        self.publish_widget.setHidden(True)

        # work out the information to display
        submitted_dict = dict()
        for job_type in job_types:
            submitted_dict[job_type] = job_types.count(job_type)

        icon_dict = dict()
        for job_type, count in submitted_dict.items():
            # create the job info and amount
            job_ids_str = f"{job_type} - x{count}"
            lbl_job_ids = QtWidgets.QLabel(job_ids_str)

            # create icon of the job type
            lbl_job_icon = QtWidgets.QLabel()
            lbl_job_icon.setFixedSize(22, 22)
            lbl_job_icon.setScaledContents(True)
            lbl_job_icon.setObjectName(job_type)

            # build the widget and add to the layout
            layout = QtWidgets.QHBoxLayout()
            layout.addWidget(lbl_job_icon)
            layout.addWidget(lbl_job_ids)
            self.info_layout.addLayout(layout)
            JOB_TYPE_TO_ICON = dict()
            # add to the dictionary
            icon_name = JOB_TYPE_TO_ICON.get(job_type, job_type)
            if icon_name:
                icon_dict[icon_name] = job_type
        self.set_widget_icons(icon_dict=icon_dict)

    def initializePage(self):
        """
        Display the published information on the page
        """
        self.set_last_page()
        deadline_mode = self.wizard().data.get("deadline_mode", False)
        if deadline_mode:
            self.build_deadline_widget(self.data["job_types"])
            return

        asset_version_id = self.wizard().asset_version_id
        if not asset_version_id:

            self.publish_widget.setHidden(True)
            font = QtGui.QFont()
            font.setPointSize(15)
            self.lbl_job_id.setFont(font)

            # if publish was an option that was skipped
            # then its successful as the task ran.
            if self.data.get("publish") is True:
                self.lbl_job_id.setText("Task Failed")
                self.lbl_job_id.setStyleSheet("color: red")
            else:
                self.lbl_job_id.setText("Task Completed")
            return

        self.submitted_widget.setHidden(True)

        # get access to the asset version and get the data
        ftver = self.wizard().ftver
        ftver.asset_version_id = asset_version_id
        self.txt_ftrack_link.setText(ftver.html_link_format)
        self.txt_ftrack_link.setOpenExternalLinks(True)

        # build asset information
        asset_version = ftver.asset_version
        for links in asset_version["link"]:
            label = QtWidgets.QLabel(links['name'])
            label.setStyleSheet("font-weight: bold")
            self.publish_info_layout.addWidget(label)

        self.txt_comment.setText(asset_version["comment"])

        # set thumbnail
        self.set_thumbnail_image(ftver.thumbnail_url)

        thumbnail_path = self.data.get("thumbnail_path")
        gif_path = self.data.get("gif_path")

        if thumbnail_path and os.path.exists(thumbnail_path):
            self.set_widget_icons(icon_dict={thumbnail_path: "thumbnail"})

        elif gif_path and os.path.exists(gif_path):
            self.set_gif_on_label(self, gif_path, self.thumbnail, 250, 150)

        # get the wip file path and add to the display
        wip_file_path = ftver.wip_file_path
        if wip_file_path:
            wip_file_name = os.path.basename(wip_file_path)
        elif self.data.get("display_name"):
            wip_file_name = self.data.get("display_name")
        else:
            wip_file_name = "-"
        self.txt_file_path.setText(wip_file_name)
        self.txt_file_path.setToolTip(wip_file_path)

    def isComplete(self):
        """ As it's the final page its complete """
        return True
