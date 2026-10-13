""" Select the movie file to publish """
import os
from CCPySide import QtWidgets, QtCore
from ccgeneral.wizard.pages.context_page import ShotContextPage


class LevelSequenceContextPage(ShotContextPage):
    title = "Publish Level Sequence"

    def __init__(self, parent=None):
        super(LevelSequenceContextPage, self).__init__(parent)

    def initializePage(self):
        """
        Set the sequences from the start directory
        """
        super().initializePage()
        self.create_movie_checkbox()

    def create_movie_checkbox(self):
        """
        Add the sequence line edit
        """
        self.chk_create_movie = QtWidgets.QCheckBox("Create Movie")
        layout = QtWidgets.QHBoxLayout()
        layout.addItem(self.create_spacer())
        layout.addWidget(self.chk_create_movie)
        layout.addItem(self.create_spacer())
        self.additional_widgets.addLayout(layout)

    def validatePage(self):
        """
        Store the thumbnail path in the wizard data
        """
        super().validatePage()
        self.data["create_movie"] = self.chk_create_movie.isChecked()
        return True
