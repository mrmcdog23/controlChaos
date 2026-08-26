""" The user setup when maya starts """
import os
import maya.cmds as cmds
import maya.mel as mel
import maya.utils as mutils
import cccore.data.server_data as server_data
import ccmaya.startup.maya_menu as maya_menu
import ccmaya.maya_constants as maya_constants
import cccore.core_constants as core_constants


START = core_constants.DEFAULT_START_FRAME
END = core_constants.DEFAULT_END_FRAME


def set_frames_per_second():
    """
    Set the project frame range pulled from ftrack
    """
    import ccmaya.startup.context_buttons as context_buttons
    ftshot = context_buttons.FTRACK_SHOT
    unit = maya_constants.FPS[ftshot.fps]
    cmds.currentUnit(time=unit)
    cmds.optionVar(cat="Settings", sv=("workingUnitTime", unit))
    cmds.playbackOptions(min=START, ast=START, max=END, aet=END)


def create_save_menu_item():
    """
    Add the save menu item to the file menu to save the file
    in the No8 structure
    """
    from pymel.core.language import MelGlobals
    mel.eval("buildFileMenu")
    main_file_menu = MelGlobals.get('$gMainFileMenu')
    cmds.menuItem(
        label="Control Chaos File Save",
        parent=main_file_menu,
        insertAfter="saveAsOptions",
        c="import ccmaya.utils.maya_utils as utils;utils.cc_save_panel_refresh()"
    )


def create_context_buttons():
    """
    Create the context buttons for setting the environment
    in the maya session
    """
    import ccmaya.startup.context_buttons as context_buttons
    ctx_btn = context_buttons.ContextButtons()
    ctx_btn.entity_button()


def create_label(pipeline_root, icon_name, text_label):
    # type: (str, str, str) -> None
    """
    Create the label on the top bar to display
    the current show and pipe version

    Args:
        pipeline_root: Root of the selected pipeline:
        icon_name: Icon to display
        text_label: The label of the text
    """
    icon_dir = os.path.join(pipeline_root, "core", "icons")
    icon_path = os.path.join(icon_dir, icon_name)
    cmds.iconTextStaticLabel(
        st="iconAndTextHorizontal",
        al="left",
        i1=icon_path,
        p="flowLayout1",
        l=text_label,
        height=28,
        fn="boldLabelFont"
    )


def create_callbacks():
    """
    Create the maya callbacks
    """
    import no8maya.startup.callbacks as callbacks
    callbacks.initialize_callbacks()


def main():
    """
    Add all no8 relevant ui and buttons
    """

    project_data = server_data.ProjectData()
    display_name = project_data.display_name
    pipeline_root = project_data.pipeline_root
    project_name = project_data.project_name
    pipeline_type = "development"

    # create the top labels
    create_label(pipeline_root, "project", project_name)
    create_label(pipeline_root, pipeline_type, "Development")

    create_save_menu_item()

    maya_menu.build_cc_menu()
    #maya_menu.build_no8_playblast_menu()
    #create_callbacks()
    create_context_buttons()
    #set_frames_per_second()


mutils.executeDeferred(main)

