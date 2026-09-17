""" Houdini node utilities """
import os
import hou
import ccftrack.shot as shot
import ccftrack.asset as asset
import ccftrack.asset_version as asset_version
import cccore.utils.file_utils as file_utils
import cccore.file_env.context_utils as context_utils
import cchoudini.utils.hou_utils as hou_utils
import cchoudini.hou_constants as hou_constants
import cchoudini.utils.create_parameters as create_parameters
import cchoudini.node.ftrack_hou_node as ftrack_hou_node
#from cchoudini.node.cccache import No8CacheNode
from typing import Optional


NO8_FRAME_RANGE = hou_constants.NO8_FRAME_RANGE


def cccache_submit(cc_cache_node):
    # type: (hou.Node) -> None
    """
    Submit the cache node locally or to Deadline

    Args:
        cc_cache_node: Cache node to submit
    """
    local_or_farm = cc_cache_node.parm("local_or_farm").eval()
    if local_or_farm == 0:
        No8CacheNode(cc_cache_node).submit()
    else:
        import cchoudini.wizard.cache_submit_wizard as cache_submit_wizard
        cache_submit_wizard.main(cc_cache_node)


def publish_cache(cc_cache_node):
    # type: (hou.Node) -> None
    """
    Submit the cache to publish

    Args:
        cc_cache_node: Cache node to submit
    """
    version_num = cc_cache_node.parm("version_padded").evalAsString()
    output_path = cc_cache_node.parm("output_path").evalAsString()
    if not os.path.exists(output_path):
        hou_utils.hou_messagebox(
            "Cache doesn't exist",
            f"Path does node exist to publish",
            "critical"
        )
        return
    ctx = context_utils.get_context_from_path(output_path)
    category = file_utils.get_category(ctx.ext)

    if ctx.is_asset:
        ftasset = asset.FtAsset()
        av = ftasset.get_build_asset_version(
            ctx.asset_build, ctx.task, version_num, category)
    else:
        ftshot = shot.FtShot()
        av = ftshot.get_shot_asset_version(
            ctx.sequence, ctx.shot, ctx.task, version_num, category)

    if av:
        hou_utils.hou_messagebox(
            "Already Published",
            f"Version {int(version_num)} is already published",
            "critical"
        )
        return
    import cchoudini.wizard.publish_cache_wizard as publish_cache_wizard
    publish_cache_wizard.main(cc_cache_node)


def update_node(node):
    # type: (hou.Node) -> None
    """
    Update the houdini node to the new asset version

    Args:
        node: Houdini node to update
    """
    ftrack_id = node.parm("ftrack_id").eval()
    ftasset_version = asset_version.FtAssetVersion()
    ftasset_version.asset_version_id = ftrack_id


def hide_parameter(node, parm_name, hide=True):
    # type: (hou.Node, str, Optional[bool]) -> None
    """
    Hide a parameter by its name

    Args:
        node: The houdini node to hide
        parm_name: Parameter name to hide
        hide: Show or hide the parameter
    """
    ptg = node.parmTemplateGroup()
    copy_parm_template = ptg.find(parm_name)
    ptg.hide(copy_parm_template, hide)
    node.setParmTemplateGroup(ptg)


def create_render_random_frames_parm(node):
    # type: (hou.Node) -> None
    """
    Add the random frames menu item. Link to the original and hide it

    Args:
        node: The render node to add the random frames to
    """
    # add the random frames menu item
    items_list = [
        "Render Current Frame",
        "Render Frame Range",
        "Render Frame Range (Strict)",
        "Random Frames"
        ]
    command = "import cchoudini.utils.node_utils as nu;nu.show_random_frames(hou.pwd())"
    create_parameters.menu_parm(
        node,
        NO8_FRAME_RANGE,
        "Value Frame Range",
        "trange",
        items_list,
        command=command
    )

    # connect expression and hide original
    expression = f'ch("{node.path()}/{NO8_FRAME_RANGE}")'
    dest_parm = node.parm("trange")
    dest_parm.setExpression(
        expression,
        language=hou.exprLanguage.Hscript,
    )
    hide_parameter(node, "trange")

    # add random frames string
    create_parameters.string_parm(
        node, "random_frames", "Random Frames", NO8_FRAME_RANGE, value="2-10,21,24,28-32")
    hide_parameter(node, "random_frames")


def show_random_frames(node):
    # type: (hou.Node) -> None
    """
    Hide of show random frames

    Args:
        node: The render node to add the random frames to
    """
    random_frames = node.parm(NO8_FRAME_RANGE).eval()
    show = random_frames == 3
    hide_parameter(node, "random_frames", not show)
    hide_parameter(node, "f", show)


def set_position_nodes(node_list, ygap=None):
    # type: (list[hou.Node], Optional[int]) -> None
    """
    Set the node positions in an  organised way

    Args:
        node_list: List of nodes to organise
        ygap: Gap between nodes vertically
    """
    row_count = 3
    xpos = 0
    ypos = 0
    ygap = ygap or -1

    count = 0
    for node in node_list:
        if count == row_count:
            ypos += ygap
            count = 0
            xpos = 0
        xpos += 2
        count += 1
        node.setPosition((xpos, ypos))


def get_current_cache_path(source_node):
    """
    Check if there is an alembic node and if there
    is then get the file parameter and its path

    Returns:
        current_cache_path: The current alembic path
        file_parameter: alembic file parameter
    """
    cache_nodes = hou_utils.find_all_subnodes_of_types(source_node, ["alembic", "file"])
    if not cache_nodes:
        return None, None

    # if there was an alembic node then get its path
    cache_node = cache_nodes[0]
    for parm_name in ["fileName", "file"]:
        file_parameter = cache_node.parm(parm_name)
        if file_parameter:
            break
    current_cache_path = file_parameter.eval()

    # if not alembic path is set check if there is a source path
    if not current_cache_path and source_node.parm("source_path"):
        current_cache_path = source_node.parm("source_path").eval()
    return current_cache_path, file_parameter


def load_published_hda(parent_node, asset_ftver, component_name, hda_path, shot_data=None):
    # type: (hou.Node, asset_version.FtAssetVersion, str, str, Optional[dict]) -> hou.Node
    """
    Args:
        parent_node: Node to create the HDA under
        asset_ftver: The HDA ftrack instance
        component_name: Name of the component to load
        hda_path: Path of the HDA to load
        shot_data: The list in order of shot data
    """
    # load a hda file by getting the definition
    definition = hou.hda.definitionsInFile(hda_path)[0]
    node_type = definition.nodeType().name()

    hda_node = parent_node.createNode(node_type, node_type)
    hda_node.setColor(hou.Color((0.0, 0.8, 0.0)))

    _, file_parameter = get_current_cache_path(hda_node)
    if not file_parameter:
        return

    # set the cache expression
    hda_node.allowEditingOfContents()
    if file_parameter.keyframes():
        file_parameter.deleteAllKeyframes()
    file_parameter.setExpression(f'chs("../{hou_constants.USE_CACHE_PARM_NAME}")')

    # add the ftrack parameters
    ftnode = ftrack_hou_node.FTrackHouNode(hda_node, asset_ftver, component_name)
    ftnode.add_ftrack_parameters()

    # set the node to shot mode to include the shot data
    if shot_data:
        ftnode.set_shot_data(shot_data)
    return hda_node
