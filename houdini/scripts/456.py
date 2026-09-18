""" Functions to run on file open """
import os
import hou
import toolutils
import ftrack_api
import cccore.utils.cc_logging as cc_logging
import cccore.file_env.context_utils as context_utils
import cchoudini.panel.create_cc_panel as create_cc_panel
import cchoudini.hou_constants as hou_constants


def get_file_names_tuple():
    # type: () -> tuple
    """
    Get a set of the file names
    """
    file_templates = hou_constants.FILE_TEMPLATES.copy()
    file_templates.append("untitled.hip")
    file_templates_set = set(file_templates)
    if "" in file_templates_set:
        file_templates_set.remove("")
    return tuple(file_templates_set)


def set_project_environment():
    """
    When a file is opened set the context panel and environment
    """
    # check houdini has opened
    logger = cc_logging.cc_logger()
    if not hou.isUIAvailable():
        return

    hou_window = hou.qt.mainWindow()
    if not hou_window:
        return

    # check there is a file open
    hip_path = hou.hipFile.path()
    if not hip_path:
        return

    # if it is a new scene skip
    if os.path.basename(hip_path) == "untitled.hip":
        return

    #  if it is a template then skip
    if "_template_" in os.path.basename(hip_path):
        return

    # check the file belongs on that project
    correct_project = context_utils.is_file_correct_for_project(hip_path)
    if not correct_project:
        hou.ui.displayMessage("File is not of this project environment!\n"
                              "Restart Houdini under the correct project.",
                              severity=hou.severityType.Error)
        return

    ctx_panel = create_cc_panel.get_ctx_panel()
    if not ctx_panel:
        logger.warning("Panel not found!")
        return
    # set the context from the file path
    try:
        ctx_panel.set_context_button_from_path(hip_path)
    except (ftrack_api.exception.NoResultFoundError, AttributeError):
        logger.info("Unable to set context from shot")
        pass


set_project_environment()

