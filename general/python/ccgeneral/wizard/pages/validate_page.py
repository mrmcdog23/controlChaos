""" Validate publish page with widget and functions """
import inspect
from typing import Any
import cccore.base_ui as base_ui
from CCPySide import QtWidgets
from ccgeneral.wizard.pages.base_page import BasePublishPage
from cccore.utils.cc_logging import cc_logger


SELECTED_COLOUR = "rgb(50, 50, 250)"
DESELECTED_COLOUR = "rgb(80, 80, 80)"
PASSED_COLOUR = "rgb(0, 150, 0)"
WARNING_COLOUR = "rgb(255, 215, 0)"
CRITICAL_COLOUR = "rgb(150, 0, 0)"
FRAME_STYLE = "background-color: {0};"


class ValidatorWidget(base_ui.WidgetBase):
    ui_name = "validator"
    icon_to_widget = {"refresh_white": "btn_refresh",
                      "information": "btn_details",
                      "fix": "btn_autofix"
                      }

    def __init__(self, parent, valid_cls, data):
        super(ValidatorWidget, self).__init__(parent, valid_cls, data)
        self.valid_cls = valid_cls(data)
        self.pw = parent
        self.is_selected = False

        self.details.setHidden(True)
        self.lbl_validator_type.setText(self.valid_cls.validator_type)
        self.btn_autofix.setHidden(not self.valid_cls.is_autofixable)

        self.connect_signals()
        self.set_status_colour()
        self.run_validation()
        self.setFixedHeight(50)

    def connect_signals(self):
        """
        Connect the signals to the widgets
        """
        self.btn_refresh.clicked.connect(self.run_validation)
        self.btn_details.clicked.connect(self.show_details)
        self.btn_autofix.clicked.connect(self.autofix)

    def autofix(self):
        """
        Run the auto-fix and re-run the validation
        """
        self.valid_cls.fix()
        self.run_validation()

    def show_details(self):
        """
        Hide or show the details of the validation
        """
        is_hidden = self.details.isHidden()
        if is_hidden:
            self.setFixedHeight(130)
        else:
            self.setFixedHeight(50)
        self.details.setHidden(not is_hidden)

    def run_validation(self):
        """
        Validate the asset and set the widget to reflect the status
        """
        self.valid_cls.validate()
        if self.valid_cls.is_valid:
            style = FRAME_STYLE.format(PASSED_COLOUR)
        else:
            style = FRAME_STYLE.format(CRITICAL_COLOUR)
        self.frame.setStyleSheet(style)
        self.details.clear()
        self.details.setText(self.valid_cls.message)
        self.pw.completeChanged.emit()

    def set_status_colour(self):
        """
        Set the widget status colour
        """
        style = FRAME_STYLE.format(DESELECTED_COLOUR)
        self.frame.setStyleSheet(style)
        self.is_selected = False


class ValidatePage(BasePublishPage):
    title = "Validate Page"
    subtitle = "Check whether the scene is valid to publish"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = None
        self.valid_widgets = list()
        self.registered_validators = list()
        self.logger = cc_logger()
        self.logger.disabled = True
        self.connect_signals()
        self.create_layout()

    def connect_signals(self):
        """
        Connect signals to widgets
        """
        self.chk_show_errored_only.toggled.connect(self.hide_valid_widgets)

    def shared_validators(self):
        """
        File of the asset validators
        """
        pass

    def asset_validators(self):
        """
        File of the asset validators
        """
        pass

    def shot_validators(self):
        """
        File of the shot validators
        """
        pass

    def hide_valid_widgets(self, hide):
        """
        Hide or show the valid widgets

        Args:
            hide: Hide the widgets if valid
        """
        for valid_widget in self.valid_widgets:
            if not hide:
                valid_widget.setHidden(False)
            elif valid_widget.valid_cls.is_valid:
                valid_widget.setHidden(hide)

    def create_layout(self):
        """
        Create the initial layout
        """
        widget = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(self.grid_layout)
        self.validator_layout.addWidget(widget)

    def initializePage(self):
        """
        Populate with the relevant validators
        """
        super().initializePage()
        if self.built_layout:
            # delete any previous widgets
            for previous_widgets in self.valid_widgets:
                self.grid_layout.removeWidget(previous_widgets)
                previous_widgets.deleteLater()

        # clear the list for repopulating
        self.valid_widgets = list()

        # create the widget
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        self.validator_layout.addWidget(widget)

        # find all valid validators
        self.gather_validators()

        for valid_cls in self.registered_validators:
            valid_widget = ValidatorWidget(self, valid_cls, self.data)
            valid_widget.setHidden(valid_widget.valid_cls.is_valid)
            layout.addWidget(valid_widget)
            self.valid_widgets.append(valid_widget)

        self.built_layout = True
        self.all_valid_so_skip()

    def all_valid_so_skip(self):
        """
        If all the validators have passed skip to the next page.
        The page doesn't fully move to the next page so hide the widgets
        """
        for valid_widget in self.valid_widgets:
            if not valid_widget.valid_cls.is_valid:
                return

        self.wdg_main_validator.setHidden(True)
        self.wizard().next()
        self.wizard().removePage(self.page_index)

    @staticmethod
    def is_registered(valid_cls, data):
        # type: (Any, dict) -> None
        """
        Whether the validate class is of the published
        type such as matching node or task

        Args:
            valid_cls:  The class of the validator
            data: Data of te publish
        """
        raise NotImplemented

    def gather_validators(self):
        """
        Find all validators to the task type
        depending on the entity
        """
        self.registered_validators = list()
        data = self.wizard().data
        self.add_validators_to_list(self.shared_validators, data)
        validator_file = self.shot_validators
        self.add_validators_to_list(validator_file, data)

    def add_validators_to_list(self, validator_file, data):
        # type: (Any, dict) -> None
        """
        Get the validator classes and check if they are valid

        Args:
            validator_file: validator file imported
            data: The project data class
        """
        for name, valid_cls in inspect.getmembers(validator_file):
            if not inspect.isclass(valid_cls):
                continue

            if name in ["class", "__class__"] or name.startswith("Base"):
                continue

            is_registered = self.is_registered(valid_cls, data)
            if not is_registered:
                continue

            if valid_cls.task_names and data["task_name"] not in valid_cls.task_names:
                continue

            # check if the asset type is to be ignored
            asset_type = data.get("asset_build_type_name", "none")
            if asset_type in valid_cls.ignore_types:
                continue

            is_deadline = self.data.get("deadline_mode")
            if valid_cls.deadline_validator and not is_deadline:
                continue
            self.registered_validators.append(valid_cls)

    def validatePage(self):
        # type: () -> bool
        """
        Always true as the page has no data to save
        """
        self.logger.disabled = False
        return True

    def isComplete(self):
        # type: () -> bool
        """
        Loop through all validators and pass if all are valid

        Returns:
            True if all are valid
        """
        for valid_widget in self.valid_widgets:
            if not valid_widget.valid_cls.is_valid:
                return False
        return True


