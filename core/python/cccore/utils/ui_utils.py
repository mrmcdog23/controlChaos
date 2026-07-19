from CCPySide import QtWidgets, QtCore, QtGui


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