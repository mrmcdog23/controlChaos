import collections
from CCPySide import QtWidgets, QtCore, QtGui
import cccore.file_env.context as context


def messagebox(title, message, msg_type, buttons=None, parent=None, launch=True):
    # type: (str, str, str, Optional[list[str]], Optional[Any], Optional[bool]) -> str
    """
    Create and display a QMessageBox

    Args:
        title: The tile of the message box
        message: Message to display
        msg_type: Type of message (warning, info or critical)
        buttons: List of button to display
        parent: The widget to parent the message box under
        launch: Whether to launch the message box

    Returns:
        button_text: The clicked button text
    """
    if not buttons:
        if msg_type in ["info", "critical", "warning"]:
            buttons = ["Ok"]
        else:
            buttons = ["Ok", "Cancel"]

    icon_dict = {"question": QtWidgets.QMessageBox.Question,
                 "info": QtWidgets.QMessageBox.Information,
                 "warning": QtWidgets.QMessageBox.Warning,
                 "critical": QtWidgets.QMessageBox.Critical
                 }
    icon = icon_dict.get(msg_type, QtWidgets.QMessageBox.Information)
    msg = QtWidgets.QMessageBox(parent)

    for button in buttons:
        msg.addButton(button, QtWidgets.QMessageBox.YesRole)

    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setWindowFlags(msg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    if not launch:
        return msg

    msg.exec()
    button_text = msg.clickedButton().text()
    return button_text


def cc_save_with_suffix(ext):
    # type: (str) -> Optional[str]
    """
    Save the file with a suffix
    """
    suffix, ok_pressed = QtWidgets.QInputDialog.getText(
        None, "Suffix", "Control Chaos Suffix Save", QtWidgets.QLineEdit.Normal)

    if "_" in suffix:
        messagebox("No Underscores", "No underscores allowed", "critical")
        return

    if ok_pressed and suffix != '':
        ctx = context.Context(overrides={"suffix": suffix, "ext": ext})
        if ctx:
            return ctx.next_save_path


def get_status_stylesheet(status):
    # type: (Any) -> str
    """
    From a ftrack status get the style sheet text

    Args:
        status: The status dictionary

    Returns:
        style_sheet: Text of the style sheet to assign
    """
    if not status:
        return str()
    status_colour = status['color']
    style_sheet = f"color: black; background-color: {status_colour}"
    return style_sheet


def context_layout_form_context(ctx):
    # type: (context.Context) -> QtWidgets.QFormLayout
    """
    Build a form layout from a context class

    Args:
        ctx: Current context class

    Returns:
        form_layout: The context layout
    """
    context_dict = collections.OrderedDict()
    if ctx.is_build:
        context_dict["Type:"] = ctx.build_type
        context_dict["Name:"] = ctx.asset_build
        context_dict["Task:"] = ctx.task
    else:
        if ctx.episode:
            context_dict["Episode:"] = ctx.episode
        context_dict["Sequence:"] = ctx.sequence
        context_dict["Shot:"] = ctx.shot
        context_dict["Task:"] = ctx.task

    form_layout = QtWidgets.QFormLayout()
    for context_key, context_value in context_dict.items():
        lbl_context_key = QtWidgets.QLabel(context_key)
        lbl_context_value = QtWidgets.QLabel(context_value)
        lbl_context_value.setFont(QtGui.QFont("Ariel", weight=QtGui.QFont.Bold))
        form_layout.addRow(lbl_context_key, lbl_context_value)
    return form_layout
