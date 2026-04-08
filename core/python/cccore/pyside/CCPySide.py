"""
Wrapper to import the correct version of pyside
"""
import os

try:
    import PySide2
    use_pyside2 = True
except ModuleNotFoundError:
    use_pyside2 = False

if use_pyside2:
    import PySide2
    import PySide2.QtGui as QtGui
    import PySide2.QtCore as QtCore
    import PySide2.QtWidgets as QtWidgets
    from PySide2.QtWidgets import QAction
    import PySide2.QtUiTools as QUiLoader
    import shiboken2 as shiboken
else:
    import PySide6
    import PySide6.QtGui as QtGui
    import PySide6.QtCore as QtCore
    import PySide6.QtWidgets as QtWidgets
    from PySide6.QtGui import QAction
    from PySide6.QtUiTools import QUiLoader
    import shiboken6 as shiboken
