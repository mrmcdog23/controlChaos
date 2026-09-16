""" Houdini scene utilities """
import os
import hou
import ccftrack.shot as shot
import cchoudini.utils.hou_utils as hou_utils
import cccore.utils.cc_logging as cc_logging
import cccore.data.server_data as server_data
import cccore.core_constants as core_constants


# constant
logger = cc_logging.cc_logger()


def lighting_template_exists():
    # type: () -> bool
    """
    Check if the lighting template already exists

    Returns:
        False if it does not exist
    """
    # check if already imported
    for out_name in ["FG", "BG", "SET"]:
        node = hou.node(f"/out/{out_name}")
        if node:
            # error if node exists
            message = f"Node name {out_name} already exists so won't import"
            hou_utils.hou_messagebox(
                "Error loading template", message, "critical")
            return True
    return False


def import_lighting_template():
    """
    Import the lighting template hip file
    """
    start_frame = 1001
    end_frame = 1200

    # check if already imported
    if lighting_template_exists():
        return
    import_template_file("lighting", start_frame, end_frame)


def import_lookdev_template():
    """
    Import the lookdev template hip file
    """
    import_template_file("lookdev")


def import_groom_template():
    """
    Import the lookdev template hip file
    """
    import_template_file("groom")


def import_template_file(template_name, start_frame=None, end_frame=None):
    # type: (str, int, int) -> None
    """
    Import the houdini template file

    Args:
        template_name: Name of the file type
        start_frame: The first frame to set to
        end_frame: The last frame to set to
    """
    start_frame = start_frame or core_constants.DEFAULT_START_FRAME
    end_frame = end_frame or core_constants.DEFAULT_END_FRAME

    # ask before importing into the scene
    buttons = ["Import Template", "Cancel"]
    response = hou_utils.hou_messagebox(
        "Import",
        f"Import {template_name} Template?",
        "question",
        buttons=buttons
    )
    if response == 1:
        return

    project_data = server_data.ProjectData()

    # get version prefix
    major, minor, patch = hou.applicationVersion()
    version = f"{major}{minor}{patch}"
    file_template_name = f"{template_name}_template_{version}.hip"

    # import and set the frame range
    template_path = os.path.join(
        project_data.houdini_template_dir, version, file_template_name
    )
    hou.hipFile.merge(template_path)
    fps = shot.FtShot().fps
    hou.setFps(fps)
    hou.playbar.setFrameRange(start_frame, end_frame)

    # final message
    message = f"{template_name} template loaded\n\n" \
              f"Frame range {start_frame}-{end_frame} \n " \
              f"Frames Per Second: {fps}"
    hou_utils.hou_messagebox("Loaded Template", message, "info")


def object_merge():
    """
    Merge one object from one context to another
    """
    logger.info(f"Merging objects...")
    # Get the selected nodes
    source_nodes = hou.selectedNodes()
    if not source_nodes:
        hou_utils.hou_messagebox(
            "Nothing Selected", "Nothing selected!", "critical")
        return

    # Show the node chooser
    result = hou.ui.selectNode(
        title="Choose Parent Node",
        node_type_filter=hou.nodeTypeFilter.Obj
    )

    if not result:
        hou.ui.setStatusMessage(
            "No parent node selected", severity=hou.severityType.Error)
        return

    # Get the parent node based on the selection
    parent_node = hou.node(result)

    # Create new geometry node for each selected node
    for source_node in source_nodes:
        selected_name = source_node.name()
        logger.info(f"Selected node name: {selected_name}")

        dest_node = parent_node.createNode("geo", selected_name)

        # Create an object merge inside the new node
        obj_merge = dest_node.createNode("object_merge")

        # Point the object merge to the selected node
        obj_merge.parm("objpath1").set(source_node.path())
        obj_merge.parm("xformtype").set("local")

        # Set the display and render flags for the new node
        dest_node.setCurrent(True, True)
        logger.info(f"dest node: {dest_node}")
        # copy the parameters from one node to the other
        for source_parm in source_node.allParms():
            parm_name = source_parm.name()
            dest_parm = dest_node.parm(parm_name)
            if not dest_parm:
                continue

            template = dest_parm.parmTemplate()
            if isinstance(template, (hou.MenuParmTemplate, hou.ToggleParmTemplate)):
                # create the expression
                expression = f'ch("{source_node.path()}/{parm_name}")'
            else:
                # create the expression
                expression = f'chs("{source_node.path()}/{parm_name}")'
            dest_parm.setExpression(
                expression,
                language=hou.exprLanguage.Hscript,
            )



