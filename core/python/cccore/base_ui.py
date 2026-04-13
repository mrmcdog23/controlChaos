""" Create uis and manager them through base class """
import os
import sys
import logging
import inspect
import requests
from typing import Any, Optional
from CCPySide import QtWidgets, QtGui, QtCore
from qtpy import uic
from pathlib import Path


CONTROL_CHAOS_SS = "../../css/cc_stylesheet.css"
BTN_SS = "../../css/btn_stylesheet.css"



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
    cc_header = None
    add_cc_title_name = False

    def __init__(self, parent=None, *args, **kwargs):
        super(Ui, self).__init__(parent)

        self._icon_directory = None
        self._cc_style_sheet = None

        self.load_ui_file_and_set_window()
        self.add_theme_directory()
        self.set_widget_icons()
        self.add_icons_to_tab()
        self.load_cc_style_sheet()
        self.apply_btn_style_sheet()

        self.load_previous_ui_settings()
        self.add_cc_header()

    def load_ui_file_and_set_window(self):
        # load the ui file. If one has already been defined use that
        ui_file_path = self.get_relevant_ui_file()
        if os.path.exists(ui_file_path):
            uic.loadUi(ui_file_path, self)

        if self.title:
            if self.add_cc_title_name:
                self.setWindowTitle(f"Control Chaos {self.title}")
            else:
                self.setWindowTitle(self.title)

        if self.window_icon:
            window_icon_path = self.get_icon_path(self.window_icon)
            qicon = QtGui.QIcon(window_icon_path)
            self.setWindowIcon(qicon)

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
        if not self.use_cc_ss:
            return
        self._cc_style_sheet = self.read_css(CONTROL_CHAOS_SS)
        if self.additional_stylesheet:
            self._cc_style_sheet += self.additional_stylesheet
        self.setStyleSheet(self._cc_style_sheet)

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

    def get_icon_path(self, icon_name):
        # type: (str) -> str
        """
        Get the icon path from the icon name and icon directory

        Args:
            icon_name: Name of the icon to find

        Returns:
            icon_path: Path to the icon
        """
        if not icon_name.endswith(".png"):
            icon_name = f"{icon_name}.png"

        # if the icon name is already a path that exists return it
        if "/" in icon_name and os.path.exists(icon_name):
             return icon_name.replace("\\", "/")

        # check the icon directory for the image
        icon_path = os.path.join(self.icon_directory, icon_name)
        if os.path.exists(icon_path):
            return icon_path.replace("\\", "/")
        
        # check the directory from when the python file is launched
        python_file_path = inspect.getfile(self.__class__)
        current_image_path = os.path.join(os.path.dirname(python_file_path), icon_name)
        if os.path.exists(current_image_path):
            return current_image_path.replace("\\", "/")

    def get_qicon_from_name(self, icon_name):
        # type: (str) -> QtGui.QIcon
        """
        From its name get a qicon

        Args:
            icon_name: Name of the icon to find
        """
        icon_path = self.get_icon_path(icon_name)
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
            self.apply_icon_to_widget(widget_name, icon_name)

    def apply_icon_to_widget(self, widget_name, icon_name):
        # type: (QtWidgets.QWidget, str) -> None
        """
        From an icon name find its path and apply to the widget

        Args:
            widget: The widget to apply the icon to
            icon_name: Name of the icon to set
        """
        if isinstance(widget_name, QtWidgets.QWidget):
            widget = widget_name
        else:
            widget = self.findChild(QtWidgets.QWidget, widget_name)
            
        # if widget does not exist return
        if not widget:
            logging.getLogger().warning(f"Can not find widget name {widget_name}")
            return

        icon_path = self.get_icon_path(icon_name)
        if not icon_path:
            logging.getLogger().warning(f"Can not find icon name {icon_name}")
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
        icon_path = self.get_icon_path(icon_name)
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
                icon_path = self.get_icon_path(icon_name)
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

    def apply_btn_style_sheet(self):
        """
        Load the cc button style sheet on to the buttons tagged with "btn_ss"
        """
        btn_style_sheet = self.read_css(BTN_SS)
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
        image_path = self.get_icon_path(image_name)
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
            if not layout_name.startswith("lyt_header"):
                continue
            if layout_name.endswith("_narrow"):
                cc_header = ControlChaosHeaderNarrow(self.title, self.window_icon)
            else:
                cc_header = ControlChaosHeader(self.title, self.window_icon)
            layout.addWidget(cc_header)
            return


class WindowBase(Ui, QtWidgets.QMainWindow):
    """ QWindow mixin """
    pass


class WidgetBase(Ui, QtWidgets.QWidget):
    """ QWidget mixin """
    pass


class WizardBase(Ui, QtWidgets.QWizard):
    """ QWizard mixin """
    pass


class WizardPageBase(Ui, QtWidgets.QWizardPage):
    """ QWizardPage mixin """
    pass


class StandaloneWindowBase(Ui, QtWidgets.QMainWindow):
    use_cc_ss = True
    add_banner = True


def open_ui(ui_class, args=None):
    # type: (Any, Optional[bool]) -> None
    """
    Function for opening standalone uis

    Args:
        ui_class: Class to open
        args: Additional arguments
    """
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()

    if args:
        window = ui_class(args=args)
    else:
        window = ui_class()
    window.show()
    app.exec_()


class ControlChaosHeader(WidgetBase):
    ui_name = "cc_header"

    def __init__(self, title, window_icon):
        # type: (str, str, bool) -> None
        """
        Daydreamer ui header

        Args:
            title: The header title text
            window_icon: The windows icon
        """
        super().__init__(title=title, window_icon=window_icon)

        # get title text upper without name in it
        self.lbl_title.setText(title.upper())

        # set the style sheet
        icon_dir_image_path = self.get_icon_path("control_chaos_logo_mid")
        style_sheet = (
            f"background-image: url('{icon_dir_image_path}');"
            f"background-repeat: no-repeat;"
            f"background-position: center;"
        )
        self.setStyleSheet(style_sheet)


class ControlChaosHeaderNarrow(ControlChaosHeader):
    ui_name = "cc_header_narrow"
    def __init__(self, title, window_icon):
        super().__init__(title=title, window_icon=window_icon)
        text = f"\n{title.upper()}"
        self.lbl_title.setText(text)
