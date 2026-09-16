""" General houdini utility functions """
import os
import re
import hou
from typing import Optional, Any
from CCPySide import QtWidgets
import cccore.file_env.context as context
import cccore.utils.ui_utils as ui_utils
import cccore.utils.file_utils as file_utils
import cccore.deadline.submit as submit
import cchoudini.node.hda as hda
import cchoudini.asset.shot_asset as shot_asset
import cchoudini.hou_constants as hou_constants
import cchoudini.panel.create_cc_panel as create_cc_panel


def launch_hou_win(win_class):
    """
    Launch the maya window

    Args:
        win_class (QMainWindow): Class of ui to open
    """
    # delete all current versions of the tool
    for inst in QtWidgets.QApplication.topLevelWidgets():
        if win_class.title == inst.windowTitle():
            inst.close()
            inst.deleteLater()

    # find and launch the ui under the maya window
    loading = win_class()
    loading.load_houdini_style_sheet()

    # move the ui to a central position
    loading.move(900, 200)

    # set the window
    loading.show()

    # set title font size
    title_widget = loading.findChild(QtWidgets.QLabel, "lbl_title")
    if title_widget:
        title_widget.setStyleSheet(f"font-size: 28pt")

    # To prevent Python from garbage collecting the label widget.
    hou.session.dummy = loading


def hou_messagebox(title, message, msg_type, buttons=None):
    # type: (str, str, str, Optional[list[str]]) -> str
    """
    Create and display a QMessageBox

    Args:
        title: The tile of the message box
        message: Message to display
        msg_type: Type of message (warning, info or critical)
        buttons: List of button to display

    Returns:
        response: The clicked button text
    """
    response = ui_utils.messagebox(title,
                                   message,
                                   msg_type,
                                   buttons=buttons,
                                   parent=hou.qt.mainWindow()
                                   )
    return response


def cc_save(prompt=True):
    # type: (Optional[bool]) -> Optional[str]
    """
    Save the file path next file

    Args:
        prompt: If True ask to save

    Returns:
        save_path: Path of the file to save
    """
    ctx = context.Context()
    if not ctx.task_dir:
        hou_messagebox("Shot Not Set", "Shot environment not set", "critical")
        return

    overrides = {"ext": "hip"}
    if prompt:
        save_path = ui_utils.cc_save_path(
            hou.qt.mainWindow(), overrides=overrides
        )
        if not save_path:
            return
    else:
        ctx = context.Context(overrides=overrides)
        save_path = ctx.next_wip_save_path
    directory = os.path.dirname(save_path)
    file_utils.create_directories(directory)
    hou.hipFile.save(save_path)

    # refresh the context panel
    panel = create_cc_panel.get_ctx_panel()
    if panel:
        panel.populate_wip_versions()

    return save_path


def is_node_hda(node):
    # type: (hou.Node) -> bool
    """
    Check whether a node is an HDA

    Args:
        node: Node to check

    Returns:
        True if the path is hda
    """
    definition = node.type().definition()
    if not definition:
        return False
    path = definition.libraryFilePath()
    return path.endswith(".hda")


def viewport_snapshot(path):
    # type: (str) -> None
    """
    Create a snapshot of the viewport

    Args:
        path: Path of the image to save
    """
    cur_desktop = hou.ui.curDesktop()

    viewer = hou.paneTabType.SceneViewer
    panetab = cur_desktop.paneTabOfType(viewer).name()
    persp = cur_desktop.paneTabOfType(viewer).curViewport().name()

    # get camera path
    desktop = cur_desktop.name()
    camera_path = f"{desktop}.{panetab}.world.{persp}"

    # get full snapshot command
    frame = hou.frame()
    snapshot_fmt = "viewwrite -f {frame} {frame} {camera_path} '{path}'"
    snapshot_cmd = snapshot_fmt.format(frame=frame, camera_path=camera_path, path=path)
    hou.hscript(snapshot_cmd)


def create_pools_menu(node):
    # type: (hou.Node) -> None
    """
    Create the deadline pools menu

    Args:
        node: Houdini node to add to
    """
    pools = submit.BaseDeadlineSubmit().pools
    ptg = node.parmTemplateGroup()
    template = hou.MenuParmTemplate("pool", "Pool",
                                    menu_items=pools,
                                    menu_labels=pools
                                    )

    index = ptg.findIndices("priority")
    ptg.insertBefore(index, template)
    node.setParmTemplateGroup(ptg)


def set_houdini_vars_from_ctx(ctx):
    # type: (context.Context) -> None
    """
    Set the houdini variables from the given context

    Args:
        ctx: Current scene context
    """
    if not ctx:
        return

    # set output name variable
    if ctx.is_asset:
        output_prefix = ctx.asset_build
    else:
        if ctx.episode:
            output_prefix = f"{ctx.episode}_{ctx.sequence}_{ctx.shot}"
        else:
            output_prefix = f"{ctx.sequence}_{ctx.shot}"
    output_name = f"{output_prefix}_{ctx.task}"

    # set the render prefix and version
    current_file_path = hou.hipFile.path()
    file_name = os.path.basename(current_file_path)
    matching_file_name = re.search(r'(.*)wip_(.*)(\d+).hip', file_name)
    if not matching_file_name:
        return

    render_prefix = matching_file_name.groups()[0]

    # job settings
    hou.hscript(f"set -g JOB = {ctx.entity_root_dir}")
    hou.hscript(f"set -g APPDATA = {ctx.appdata_dir}")

    # set sequence
    if ctx.episode:
        hou.hscript(f"set -g EP = {ctx.episode}")
    hou.hscript(f"set -g SEQ = {ctx.sequence}")
    hou.hscript(f"set -g SHOT = {ctx.shot}")

    # set the build
    hou.hscript(f"set -g BUILD = {ctx.asset_build}")

    # set task and version
    hou.hscript(f"set -g TASK = {ctx.task}")

    # if render version has been set use that
    # if not fall back to the context version
    hou.hscript(f"set -g VER = {ctx.version_padded}")

    # set output variables
    hou.hscript(f"set -g OUTPUT_NAME = {output_name}")
    hou.hscript(f"set -g OUTPUT_PREFIX = {output_prefix}")
    hou.hscript(f"set -g CURRENT_FILE_PATH = {current_file_path}")

    # set the render prefix and version
    hou.hscript(f"set -g RENDER_PREFIX = {render_prefix}")
    hou.hscript(f"set -g RENDER_VERSION = {ctx.version_padded}")


def input_nodes_of_type(base_node, node_type_names=None):
    # type: (hou.Node, Optional[list[str]]) -> list[hou.Node]
    """
    Get a list of all nodes in the node tree

    Args:
        base_node: The base node with inputs
        node_type_names: List of node name types

    Returns:
        input_nodes: List of nodes
    """
    input_nodes = list()
    for input_node in base_node.inputAncestors():
        node_type_name = input_node.type().name()
        if not node_type_names:
            input_nodes.append(input_node)
        elif node_type_name in node_type_names:
            input_nodes.append(input_node)
    return input_nodes


def copy_path(node, parm_name):
    # type: (hou.Node, str) -> None
    """
    Copy a nodes parameter value as a string to a clipboard

    Args:
        node: The node to evaluate
        parm_name: Name of the parameter
    """
    path = node.parm(parm_name).evalAsString()
    directory = os.path.dirname(path)
    QtWidgets.QApplication.clipboard().setText(directory)


def find_subnode_of_type(node, node_type):
    # type: (hou.Node, str) -> hou.Node
    """
    Find a node of a certain type in a subnetwork

    Args:
        node: Parent houdini node
        node_type: Node type to find

    Returns:
        subnode: Subtype node found
    """
    for subnode in node.allSubChildren():
        if subnode.type().name() == node_type:
            return subnode


def find_all_subnodes_of_types(node, node_types):
    # type: (hou.Node, list[str]) -> list[hou.Node]
    """
    Find a nodes of a certain types in a subnetwork

    Args:
        node: Parent houdini node
        node_types: Node type to find

    Returns:
        sub_nodes: Subtype nodes found
    """
    sub_nodes = list()
    for subnode in node.allSubChildren():
        if subnode.type().name() in node_types:
            sub_nodes.append(subnode)
    return sub_nodes


def update_menu_list(node, parm_name, list_items):
    # type: (hou.Node, str, list[str]) -> None
    """
    Update a menu item list.

    Args:
        node: houdini node to set
        parm_name: Name of the menu parameter
        list_items: List of items to add
    """
    ptg = node.parmTemplateGroup()
    menu_parm = node.parm(parm_name)
    template = menu_parm.parmTemplate()
    template.setMenuItems(list_items)
    template.setMenuLabels(list_items)
    ptg.replace(parm_name, template)
    node.setParmTemplateGroup(ptg)


def set_menu_text(node, parm_name, value):
    # type: (hou.Node, str, str) -> None
    """
    Set the houdini menu parameter value

    Args:
        node: The node to set value
        parm_name: Name of the parameter to change
        value: Text to set of the menu item
    """
    menu_parm = node.parm(parm_name)
    template = menu_parm.parmTemplate()
    items = template.menuItems()
    if value not in items:
        return
    index = items.index(value)
    node.parm(parm_name).set(index)


def get_menu_label(node, parameter):
    # type: (hou.Node, str) -> str
    """
    Get the label value
    """
    parameter = node.parm(parameter)
    labels = list(parameter.menuLabels())
    label_value = labels[parameter.eval()]
    return label_value


def hda_make_local():
    """
    Make the selected node local
    """
    nodes = hou.selectedNodes()
    if not nodes:
        return
    hda.HDA(nodes[0]).make_local()


def hda_remove_local():
    """
    Remove local definitions from the hda
    """
    nodes = hou.selectedNodes()
    if not nodes:
        return
    hda.HDA(nodes[0]).remove_local_definitions()


def set_hda_to_latest():
    """
    Remove local definitions from the hda
    """
    nodes = hou.selectedNodes()
    if not nodes:
        return
    hda.HDA(nodes[0]).set_to_latest()


def get_current_tab():
    # type: () -> hou.paneTabType.NetworkEditor
    """
    Get the current context tab
    """
    network_tabs = [t for t in hou.ui.paneTabs()
                    if t.type() == hou.paneTabType.NetworkEditor
                    ]
    if network_tabs:
        for tab in network_tabs:
            if tab.isCurrentTab():
                return tab
    return None


def get_rop_type(node_type):
    # type: (str) -> tuple
    """
    Get all rop nodes of a type

    Args:
        node_type: Type to find

    Returns:
        Rop nodes of that type
    """
    return hou.ropNodeTypeCategory().nodeType(node_type).instances()


def get_sop_type(node_type):
    # type: (str) -> tuple
    """
    Get all sop nodes of a type

    Args:
        node_type: Type to find

    Returns:
        Sop nodes of that type
    """
    return hou.sopNodeTypeCategory().nodeType(node_type).instances()


def set_parm_value(node, parm_name, value):
    # type: (hou.Node, str, str) -> None
    """
    Set a node parameter value and unlock and lock

    Args:
        node: Node to set
        parm_name: Name of the parameter to set
        value: The value to set
    """
    node.parm(parm_name).lock(False)
    node.parm(parm_name).set(value)
    node.parm(parm_name).lock(True)


def get_frame_range(node, range_parm=None, start_parm=None, end_parm=None):
    # type: (hou.Node, Optional[str], Optional[str], Optional[str]) -> (int, int)
    """
    Get the frame range of the cache node

    Args:
        node: Node to get the range from
        range_parm: Name of the selected frame range type
        start_parm: Start frame parameter name
        end_parm: End frame parameter name

    Returns:
        start: The first frame to cache
        end: The end frame to cache
    """
    range_parm = range_parm or "trange"
    start_parm = start_parm or "f1"
    end_parm = end_parm or "f2"

    # get the alembic cache frame range
    current_frame = int(hou.frame())
    trange = node.parm(range_parm)
    if trange and trange.eval() == 0:
        start = current_frame
        end = current_frame
    else:
        start = int(node.parm(start_parm).eval())
        end = int(node.parm(end_parm).eval())
    return start, end


def get_random_frames_value(node):
    # type: (hou.Node) -> Optional[str]
    """
    Get the cc random frames value

    Args:
        node: The node to get frame string

    Returns:
        The random frame string
    """
    # account for random frame ranges
    cc_custom_parm = node.parm(hou_constants.NO8_FRAME_RANGE)
    if cc_custom_parm and cc_custom_parm.evalAsString() == "Random Frames":
        return node.parm("random_frames").evalAsString()


def get_maximum_frame_range_for_ass_job(arnold_rops):
    # type: (list[hou.Node]) -> (int, int)
    """
    Get the maximum start and end frame from a list of arnold nodes

    Args:
        arnold_rops: List of rop nodes

    Returns:
        The start and end maximum frame
    """
    all_frames = list()
    random_frames_value = str()
    for arnold_rop in arnold_rops:
        random_frames_value = get_random_frames_value(arnold_rop)
        if random_frames_value:
            for random_frame_range in random_frames_value.split(","):
                all_frames.extend(random_frame_range.split("-"))
        else:
            start, end = get_frame_range(arnold_rop)
            all_frames.extend([start, end])

    if len(arnold_rops) == 1 and random_frames_value:
        frame_range = random_frames_value
    else:
        all_frames_int = [int(frame) for frame in all_frames]
        frame_range = f"{min(all_frames_int)}-{max(all_frames_int)}"
    return frame_range


def set_rop_frame_range(rop, start, end):
    # type: (hou.Node, int, int) -> None
    """
    Set a rop frame range by delete any keys first

    Args:
        rop: The rop node to set
        start: First frame to set
        end: Last frame to set
    """
    rop.parm("f1").deleteAllKeyframes()
    rop.parm("f1").set(start)
    rop.parm("f2").deleteAllKeyframes()
    rop.parm("f2").set(end)


def create_network_box(nodes, title, colour=None):
    # type: (list[hou.Node], str, hou.Color) -> hou.NetworkBox
    """
    Create a network box around a list of nodes

    Args:
        nodes: List of nodes to create the box around
        title: Text to display on the top of the box
        colour: Colour to set the background

    Returns:
        box: Network box created round the nodes
    """
    parent = None
    first_node = None
    for node in nodes:
        try:
            parent = node.parent()
            first_node = node
        except hou.ObjectWasDeleted:
            continue
        if first_node:
            break

    if not first_node:
        return

    box = parent.createNetworkBox()
    box.setPosition(first_node.position())

    # add all nodes to the box
    for node in nodes:
        box.addItem(node)

    # set color and title
    if colour:
        box.setColor(colour)
    box.setComment(title)
    box.fitAroundContents()
    return box


def get_shot_asset_nodes():
    # type: () -> list[hou.Node]
    """
    Get a list of ftrack nodes then any imported nodes

    Returns:
        shot_asset_nodes: List of houdini nodes
    """
    shot_asset_nodes = list()

    # get all ftrack nodes first
    for node in hou.node("/obj/").allSubChildren():
        if node.parm("ftrack_id"):
            shot_asset_nodes.append(node)

    alembicarchive = None
    for node in hou.node("/obj/").allSubChildren():
        if node in shot_asset_nodes:
            continue

        if node.parent() in shot_asset_nodes:
            continue

        # skip all nodes without a file name
        file_name_parm = node.parm("use_cache_path")
        if not file_name_parm:
            continue

        # find the parent of all the subpaths
        if node.type().name() == "alembicarchive":
            alembicarchive = node.path()
        elif alembicarchive and alembicarchive in node.path():
            continue
        else:
            alembicarchive = None

        shot_asset_nodes.append(node)
    return shot_asset_nodes


def get_shot_assets(session=None):
    # type: (Any) -> dict[Any, shot_asset.ShotAsset]
    """
    Get all shot assets that are ftrack related and referenced

    Args:
        session: Current ftrack session

    Returns:
        shot_assets_dict: Dict of published assets
    """
    shot_asset_nodes = get_shot_asset_nodes()
    shot_assets_dict = dict()
    for node in shot_asset_nodes:
        asset = shot_asset.ShotAsset(node=node, session=session)
        if not session:
            session = asset.ftver.session
        shot_assets_dict[asset.component_name] = asset
    return shot_assets_dict


def set_camera_viewport(camera_path):
    # type: (str) -> None
    """
    Set the viewport based on the path

    Args:
        camera_path: Path of the camera node
    """
    if not hou.isUIAvailable():
        return
    desktop = hou.ui.curDesktop()
    viewer = desktop.paneTabOfType(hou.paneTabType.SceneViewer)
    viewport = viewer.findViewport('persp1')
    viewport.setCamera(camera_path)
