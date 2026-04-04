""" Create uis and manager them through base class """
import os
import sys
import inspect
import requests
from typing import Any, Optional
from PySide6 import QtWidgets, QtGui, QtCore
from qtpy import uic
from pathlib import Path


cc_SS = "../../style/css/cc_stylesheet.css"
BTN_SS = "../../style/css/cc_button.css"
HOU_BTN_SS = "../../style/css/cc_houdini_button.css"
HOUDINI_SS = "../../style/css/houdini.css"
BLENDER_SS = "../../style/css/blender.css"
FTRACK_SS = "../../style/css/equalizer.css"
FLAME_SS = "../../style/css/flame.css"


class Ui(object):
    """ Base class for building uis """
    title = None
    icon_to_widget = dict()
    ui_name = None
    window_icon = str()
    tab_to_icons = dict()
    additional_stylesheet = None
    use_cc_ss = False
    previous_ui_settings = None

    def __init__(self, parent=None, *args, **kwargs):
        super(Ui, self).__init__(parent)
        self.cc_header = None
        self.cc_ss = kwargs.get("cc_ss")
        if self.cc_ss is None:
            self.cc_ss = self.use_cc_ss

        self._icon_directory = None
        self._cc_style_sheet = None

        # if it is a tree or table widget item skip the setup
        if isinstance(self, (QtWidgets.QTreeWidgetItem, QtWidgets.QTableWidget)):
            return

        # load the ui file. If one has already been defined use that
        ui_file_path = self.get_relevant_ui_file()
        if os.path.exists(ui_file_path):
            uic.loadUi(ui_file_path, self)

        if self.title:
            self.setWindowTitle(self.title)

        if self.window_icon:
            window_icon_path = self.get_path(self.window_icon)
            qicon = QtGui.QIcon(window_icon_path)
            self.setWindowIcon(qicon)

        self.set_project_widgets()
        self.add_theme_directory()
        self.set_widget_icons()
        self.add_icons_to_tab()
        #self.load_cc_style_sheet()
        #self.apply_btn_style_sheet()
        self.load_previous_ui_settings()
        self.add_cc_header()

    def set_project_widgets(self):
        """
        Set the project widgets icon and name
        """
        self.set_widget_icons({"project": "lbl_icon_project"})
        project_name = os.environ.get("PROJECT_NAME")
        lbl_project_name = self.findChild(QtWidgets.QLabel, "lbl_project_name")
        if lbl_project_name and project_name:
            lbl_project_name.setText(project_name)

    def check_subclasses_for_ui_file(self, subclass):
        # type: (Any) -> str
        """
        Check all subclasses for the ui file

        Args:
            subclass: Subclass to check

        Returns:
            ui_file_path: Path of the ui file if found
        """
        ui_file_path = str()
        for base_cls in subclass.__bases__:
            ui_file_path = self.get_ui_file_from_class(base_cls)
            if os.path.exists(ui_file_path):
                break
        return str(ui_file_path)

    def get_relevant_ui_file(self):
        """
        Find the .ui file to load into the class.
        Different steps to find it

        1. If the ui_name is set use that
        2. Check the current class for a file next to it
        3. Loop through all base classes for the ui file
        """
        python_file_path = inspect.getfile(self.__class__)
        if self.ui_name:
            ui_directory = os.path.dirname(python_file_path)
            ui_file_path = os.path.join(ui_directory, self.ui_name + ".ui")
        else:
            ui_file_path = self.get_ui_file_from_class(self.__class__)

        # if the path is not found loop through base classes
        if not os.path.exists(ui_file_path):
            ui_file_path = self.check_subclasses_for_ui_file(self.__class__)
            if not os.path.exists(ui_file_path):
                for subclass in self.__class__.__bases__:
                    ui_file_path = self.check_subclasses_for_ui_file(subclass)
                    if not os.path.exists(ui_file_path):
                        break
        return ui_file_path

    @staticmethod
    def get_ui_file_from_class(base_cls):
        # type: (Any) -> str
        """
        From a class get the python file path and get the
        .ui file from that as it will match the file name.

        Args:
            base_cls: The class to get the ui file for

        Returns:
            ui_file_path: Path of the ui file
        """
        python_file_path = inspect.getfile(base_cls)
        ui_file_name, _ = os.path.splitext(python_file_path)
        ui_file_path = ui_file_name + ".ui"
        return ui_file_path

    @staticmethod
    def read_css(ss_path):
        # type: (str) -> str
        """
        Read and return a style sheet content

        Args:
            ss_path: Path of the css file

        Returns:
            The style sheet text
        """
        directory = os.path.dirname(__file__)
        css_file_path = os.path.join(directory, ss_path)
        return open(css_file_path).read()

    @staticmethod
    def add_theme_directory():
        """
        Add the theme directory to the search paths
        """
        file_path = Path(__file__)
        pipeline_root_dir = file_path.parents[2]
        theme_dir = f"{pipeline_root_dir}/style/theme"
        QtCore.QDir.addSearchPath("icon", theme_dir)

    def stay_on_top(self):
        """
        Keep ui on top
        """
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

    def load_cc_style_sheet(self):
        """
        Load the cc Animation style sheet on to the current ui
        """
        self._cc_style_sheet = self.read_css(cc_SS)
        if self.cc_ss:
            if self.additional_stylesheet:
                self._cc_style_sheet += self.additional_stylesheet
            self.setStyleSheet(self._cc_style_sheet)

    def load_blender_style_sheet(self):
        """
        Load the Blender stylesheet on to the current ui
        """
        self.setStyleSheet(self.read_css(BLENDER_SS))

    def load_houdini_style_sheet(self):
        """
        Load the Houdini stylesheet on to the current ui
        """
        self.setStyleSheet(self.read_css(HOUDINI_SS))

    def load_ftrack_style_sheet(self):
        """
        Load the FTrack stylesheet on to the current ui
        """
        self.setStyleSheet(self.read_css(FTRACK_SS))

    @staticmethod
    def lw_items_text(listwidget):
        # type: (QtWidget.QListWidget) -> list[str]
        """
        From a list widget get all the items text

        Args:
            listwidget: Widget to get items

        Returns:
            List of text in the items
        """
        return [listwidget.item(x).text() for x in range(listwidget.count())]

    @property
    def icon_directory(self):
        # type: () -> str
        """
        Set the icons directory from the core variable as
        the launcher ui uses it. After the project is launched
        it will change the variable.

        Returns:
            self._icon_directory: Path to the icons directory
        """
        if not self._icon_directory:
            self._icon_directory = os.path.join(os.environ["PIPELINE_ROOT"], "core", "icons")
        return self._icon_directory

    def get_path(self, icon_name):
        # type: (str) -> str
        """
        Get the icon path from the icon name and icon directory

        Args:
            icon_name: Name of the icon to find

        Returns:
            icon_path: Path to the icon
        """
        icon_path = os.path.join(self.icon_directory, icon_name + ".png")
        return icon_path

    def get_qicon_from_name(self, icon_name):
        # type: (str) -> QtGui.QIcon
        """
        From its name get a qicon

        Args:
            icon_name: Name of the icon to find
        """
        icon_path = self.get_path(icon_name)
        return QtGui.QIcon(icon_path)

    def set_thumbnail_image(self, image_path=None):
        # type: (Optional[str]) -> None
        """
        Set the thumbnail url to the thumbnail label.
        Use the missing thumbnail if one is not provided

        Args:
            image_path: Path of the thumbnail url or image
        """
        is_url = image_path and "ftrackapp.com" in image_path
        if is_url:
            # set the url image to a widget
            data = requests.get(image_path).content
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(data)
            self.thumbnail.setPixmap(pixmap)

        # set the image
        elif not image_path or not os.path.exists(image_path):
            self.set_widget_icons({"no_thumbnail.png": self.thumbnail})
        else:
            self.set_widget_icons({image_path: self.thumbnail})

    def set_widget_icons(self, icon_dict=None):
        # type: (Optional[dict]) -> None
        """
        Set the icons to the widgets based
        on the icon and widget names
        """
        use_icon_to_widget = icon_dict if icon_dict else self.icon_to_widget
        for icon_name, widget_name in use_icon_to_widget.items():

            if isinstance(widget_name, QtWidgets.QWidget):
                widget = widget_name
            else:
                widget = self.findChild(QtWidgets.QWidget, widget_name)

            icon_dir_image_path = self.get_path(icon_name)

            # the given python file path
            python_file_path = inspect.getfile(self.__class__)
            current_image_path = os.path.join(os.path.dirname(python_file_path), icon_name + ".png")

            # find the icon path
            icon_path = None
            if "/" in icon_name and os.path.exists(icon_name):
                icon_path = icon_name

            elif os.path.exists(icon_dir_image_path):
                icon_path = icon_dir_image_path

            elif os.path.exists(current_image_path):
                icon_path = current_image_path

            if not icon_path:
                return

            if hasattr(widget, "setIcon"):
                qicon = QtGui.QIcon(icon_path)
                widget.setIcon(qicon)

            elif hasattr(widget, "setPixmap"):
                pixmap = QtGui.QPixmap(icon_path)
                widget.setPixmap(pixmap)

    def add_icons_to_combo(self, combobox, icons_list):
        # type: (QtWidgets.QComboBox, list[str]) -> None
        """
        Add icons to the combobox items

        Args:
            combobox: The combobox widget to add icons to
            icons_list: List of icons in order to add
        """
        for index, pipeline_type in enumerate(icons_list):
            icon_name = pipeline_type.lower()
            self.add_icon_to_combo_item(combobox, icon_name, index)

    def add_icon_to_combo_item(self, combobox, icon_name, index):
        # type: (QtWidgets.QComboBox, str, int) -> None
        """
        Add an icon to a combobox item

        Args:
            combobox: The combobox widget to add icons to
            icon_name: Name of the icon to set
            index: Index number of the item
        """
        icon_path = self.get_path(icon_name)
        qicon = QtGui.QIcon(icon_path)
        combobox.setItemIcon(index, qicon)

    @staticmethod
    def set_combobox_index(combobox, text):
        # type: (QtWidgets.QComboBox, str) -> None
        """
        Set the combobox index based on the text

        Args:
            combobox: The combobox that needs setting
            text: THe text to find in the combobox
        """
        index = combobox.findText(text)
        if index != -1:
            combobox.setCurrentIndex(index)

    def add_icons_to_tab(self):
        """
        Add icons to the tab widgets
        """
        if not self.tab_to_icons:
            return
        for tab_name, icons in self.tab_to_icons.items():
            tab_widget = self.findChild(QtWidgets.QTabWidget, tab_name)
            for index, icon_name in enumerate(icons):
                icon_path = self.get_path(icon_name)
                qicon = QtGui.QIcon(icon_path)
                tab_widget.setTabIcon(index, qicon)

    @staticmethod
    def filter_list_widget(list_widget, text):
        # type: (QtWidgets.QListWidget, str) -> None
        """
        Filter list widget items with given text

        Args:
            list_widget: Widget to filter
            text: Match the text of an item
        """
        for index in range(list_widget.count()):
            item = list_widget.item(index)
            if not text:
                hide = False
            else:
                hide = not text.lower() in item.text().lower()
            item.setHidden(hide)

    def apply_style_sheet_to_widgets(self, widgets):
        # type: (list[QtWidgets.QWidget]) -> None
        """
        Apply style sheet to list of widgets

        Args:
            widgets: List of QWidgets
        """
        for widget in widgets:
            widget.setStyleSheet(self._cc_style_sheet)

    def apply_btn_style_sheet(self, use_btn=None):
        # type: (Optional[QtWidgets.QPushButton]) -> None
        """
        Load the cc button style sheet on to the buttons tagged with "btn_ss"

        Args:
            use_btn: Button to apply stylesheet to
        """
        if os.environ.get("APP_NAME") == "houdini":
            btn_style_sheet = self.read_css(HOU_BTN_SS)
        else:
            btn_style_sheet = self.read_css(BTN_SS)

        if use_btn:
            use_btn.setStyleSheet(btn_style_sheet)
            return

        for btn in self.findChildren(QtWidgets.QPushButton):
            if btn.property("btn_ss") is not None:
                btn.setStyleSheet(btn_style_sheet)

    def save_previous_ui_settings(self):
        """
        Save any previous ui settings if defined
        """
        if self.previous_ui_settings:
            self.save_ui_settings(self.previous_ui_settings)

    def load_previous_ui_settings(self):
        """
        Load any previous ui settings if defined
        """
        if self.previous_ui_settings:
            self.load_ui_settings(self.previous_ui_settings)

    @staticmethod
    def create_spacer(width=None, horizontal=True):
        # type: (Optional[int], Optional[bool]) -> QtWidgets.QSpacerItem
        """
        Create a horizontal spacer item

        Args:
            width: The width of the space item
            horizontal: If True make horizontal

        Returns:
            spacer: The created spacer item
        """
        if width:
            expand = QtWidgets.QSizePolicy.Minimum
        else:
            width = 40
            expand = QtWidgets.QSizePolicy.Expanding

        args = [width, 20] if horizontal else [20, width]
        args.extend([expand, QtWidgets.QSizePolicy.Expanding])
        spacer = QtWidgets.QSpacerItem(*args)
        return spacer

    @staticmethod
    def create_completer(widget, items_list=None):
        # type: (QtWidgets.QComboBox, Optional[list[str]]) -> QtCore.QStringListModel
        """
        Create a QCompleter with for line edits or combo boxes

        Args:
            widget: Combobox to set completer to
            items_list: List of items to add

        Returns:
            completer: Model of completer to use
        """
        completer = QtWidgets.QCompleter([])
        completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.setMaxVisibleItems(10)
        completer.setFilterMode(QtCore.Qt.MatchContains)
        widget.setCompleter(completer)
        if items_list:
            model = completer.model()
            model.setStringList(items_list)
        return completer

    @staticmethod
    def set_widget_font_size(widget, font_size):
        # type: (QtWidgets.QWidget, int) -> None
        """
        Set the font size on the widgets

        Args:
            widget: The widget to the set font
            font_size: Size of the font
        """
        style_sheet = f"font-size: {font_size}pt"
        widget.setStyleSheet(style_sheet)

    @staticmethod
    def set_gif_on_label(parent, gif_path, label_wdg, width, height):
        # type: (QtWidgets.QWidget, str, QtWidgets.QWidget, int, int) -> QtGui.QMovie
        """
        Set the generated gif in the window

        Args:
            parent: The parent window or widget
            gif_path: Path of the gif to set
            label_wdg: Label to set the gif to
            width: Width to set on the gif
            height: Height of the gif

        Returns:
             movie: The movie made
        """
        movie = QtGui.QMovie(gif_path, QtCore.QByteArray(), parent)
        size = movie.scaledSize()
        size.scale(QtCore.QSize(width, height), QtCore.Qt.AspectRatioMode.IgnoreAspectRatio)
        movie.setScaledSize(size)
        movie.setCacheMode(QtGui.QMovie.CacheAll)
        movie.setSpeed(100)
        label_wdg.setMovie(movie)
        movie.start()
        return movie

    def set_background_image(self, widget, image_name):
        # type: (QtWidgets.QWidget, str) -> None
        """
        Sets the background of the widgets

        Args:
            widget: The widget to add the background to
            image_name: The image to apply
        """
        style_sheet = ("background-repeat: no-repeat;"
                       "background-position: center;"
                       )
        image_path = self.get_path(image_name)
        style_sheet += f'background-image: url("{image_path}");'
        widget.setStyleSheet(style_sheet)

    def move_to_screen_center(self):
        """
        Move the ui to the center of the screen
        """
        try:
            resolution = QtWidgets.QDesktopWidget().screenGeometry()
        except AttributeError:
            return
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def save_ui_settings(self, ui_settings):
        # type: (QtCore.QSettings) -> None
        """
        Load the ui settings from the QSettings instance

        Args:
            ui_settings: The settings class
        """
        for wdg in self.findChildren(QtWidgets.QWidget):
            key = wdg.objectName()
            if isinstance(wdg, QtWidgets.QLineEdit):
                ui_settings.setValue(key, wdg.text())

            elif isinstance(wdg, QtWidgets.QSpinBox):
                ui_settings.setValue(key, wdg.value())

            elif isinstance(wdg, QtWidgets.QDateEdit):
                ui_settings.setValue(key, wdg.date())

            elif isinstance(wdg, QtWidgets.QComboBox):
                ui_settings.setValue(key, wdg.currentText())

    def load_ui_settings(self, ui_settings):
        # type: (QtCore.QSettings) -> None
        """
        From the given QSettings instance find
        the widget names and set the values

        Args:
            ui_settings: The settings class
        """
        for widget_name in ui_settings.allKeys():
            wdg = self.findChild(QtWidgets.QWidget, widget_name)
            if not wdg:
                continue

            value = ui_settings.value(widget_name)
            if value is None:
                continue

            if isinstance(wdg, QtWidgets.QLineEdit):
                wdg.setText(value)
            elif isinstance(wdg, QtWidgets.QSpinBox):
                wdg.setValue(int(value))
            elif isinstance(wdg, QtWidgets.QComboBox):
                self.set_combobox_index(wdg, value)

    def add_cc_header(self):
        """
        Find the header layout and add to the ui
        """
        for layout in self.findChildren(QtWidgets.QLayout):
            layout_name = layout.objectName()
            if layout_name.startswith("cc_header"):
                allow_spaces = layout_name.endswith("_narrow")
                self.cc_header = ccHeader(
                    self.title, self.window_icon, allow_spaces)
                layout.addWidget(self.cc_header)
                return


class WindowBase(Ui, QtWidgets.QMainWindow):
    """
    QWindow mixin
    """
    pass


class WidgetBase(Ui, QtWidgets.QWidget):
    """ QWidget mixin """
    pass


class WizardBase(Ui, QtWidgets.QWizard):
    """
    QWizard mixin
    """
    pass


class WizardPageBase(Ui, QtWidgets.QWizardPage):
    """
    QWizardPage mixin
    """
    pass


def open_ui(ui_class, cc_ss=False, args=None):
    # type: (Any, Optional[bool], Optional[bool]) -> None
    """
    Function for opening standalone uis

    Args:
        ui_class: Class to open
        cc_ss: Whether to apply the cc stylesheet
        args: Additional arguments

    Returns:

    """
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()

    if args:
        window = ui_class(cc_ss=cc_ss, args=args)
    else:
        window = ui_class(cc_ss=cc_ss)

    window.show()
    app.exec_()


class ccHeader(WidgetBase):
    icon_to_widget = {"cc_yellow": "lbl_cc_icon",
                      }
    ui_name = "cc_header"

    def __init__(self, title, window_icon, allow_spaces):
        # type: (str, str, bool) -> None
        """
        Daydreamer ui header

        Args:
            title: The header title text
            window_icon: The windows icon
        """
        super().__init__(title=title, window_icon=window_icon, allow_spaces=allow_spaces)
        spaced_title = str()
        for character in title:
            if not allow_spaces and character == " ":
                spaced_title += "\n"
            else:
                spaced_title += f" {character.upper()}"
        self.lbl_title.setText(spaced_title)

        if window_icon:
            self.set_widget_icons(
                icon_dict={window_icon: self.tool_icon}
            )


def open_maya_ui(ui_class, *args, **kwargs):
    """
    Open a maya window

    Args:
        ui_class: Ui class to open
        *args: Additional arguments
        **kwargs: Additional optional arguments
    """
    main = ui_class()
    main.show()











