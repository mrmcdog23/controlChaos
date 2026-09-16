""" Functions to run on file open """
import os
import hou
import toolutils
import ftrack_api
import ccftrack.shot as shot
import cccore.utils.cc_logging as cc_logging
import cccore.file_env.context_utils as context_utils
import cchoudini.utils.flipbook_utils as flipbook_utils
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


def set_ocio_colour_space():
    """
    Set the render view colourspace
    """
    panel = hou.ui.paneTabOfType(hou.paneTabType.IPRViewer)
    if not panel:
        return
    if shot.FtShot().is_commercial:
        panel = hou.ui.paneTabOfType(hou.paneTabType.IPRViewer)
        panel.setOCIODisplayView(
            display="ACES",
            view="Rec.709"
        )
        return
    panel = hou.ui.paneTabOfType(hou.paneTabType.IPRViewer)
    panel.setOCIODisplayView(
        display="Rec.1886 Rec.709 - Display",
        view="ACES 1.0 - SDR Video (D60 sim on D65)"
    )


def run_colour_space():
    """
    Set the ocio colour space on the viewer
    """
    if not hou.isUIAvailable():
        return
    import hdefereval
    hdefereval.executeDeferred(lambda: set_ocio_colour_space())
    hdefereval.executeDeferred(lambda: flipbook_utils.set_flipbook_output())


run_colour_space()
set_project_environment()

