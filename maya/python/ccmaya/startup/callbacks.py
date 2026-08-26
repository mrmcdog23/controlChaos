""" initialize the maya callbacks """
import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
import no8maya.startup.context_buttons as context_buttons
import no8maya.maya_constants as maya_constants
import no8core.utils.context_utils as context_utils
import no8core.core_constants as core_constants
import no8core.context as context
import no8core.utils.backup_file as backup_file


START = core_constants.DEFAULT_START_FRAME
END = core_constants.DEFAULT_END_FRAME


def convert_camera_callback(node_name):
    # type: (str) -> None
    """
    Create item for a standard maya camera to a
    no8 camera triggered from the outliner.

    Args:
        node_name: Selected node name
    """
    object_type = cmds.objectType(node_name)

    # it will most likely be a transform selected
    # and if so check the shape is a camera
    if object_type == "transform":
        try:
            shape = cmds.listRelatives(node_name, s=True)[0]
        except IndexError:
            return
        # if the shape is not a camera then return
        if cmds.objectType(shape) != "camera":
            return

    # if the object is not a camera or transform then return
    elif object_type != "camera":
        return

    # if it is already a no8 camera return
    if cmds.objExists(f"{node_name}.ftrackId"):
        return

    # build the menu item in the outliner
    command = f"import no8maya.camera.camera_convert as cc;" \
              f"cc.CameraConversion('{node_name}').convert_cam_to_no8_cam()"
    cmds.menuItem(divider=True, insertAfter="")
    cmds.menuItem(
        "convert_no8_camera",
        enableCommandRepeat=False,
        label="Convert To No8Camera",
        command=command
    )


def initialize_callbacks():
    """
    Create the open and new maya callbacks
    """
    OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterSave, save_backup_file)
    OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterOpen, set_context_buttons)
    OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterNew, set_scene_fps)

    # add camera convert callback
    cmds.callbacks(
        addCallback=convert_camera_callback,
        hook='addItemsToOutlinerNodePopupMenu',
        owner="camera_con"
    )


def save_backup_file(*args, **kwargs):
    """
    Save a backup of the file path
    """
    maya_file_path = cmds.file(q=True, sn=True)
    backup_file.create_backup_file(maya_file_path)


def set_scene_fps(*args, **kwargs):
    """
    Set the project frame range pulled from ftrack
    """
    ftshot = context_buttons.FTRACK_SHOT
    unit = maya_constants.FPS[ftshot.fps]
    cmds.currentUnit(time=unit)
    cmds.playbackOptions(min=START, ast=START, max=END, aet=END)


def set_context_buttons(*args, **kwargs):
    """
    Set the shot context buttons when a file is opened
    """
    if cmds.about(batch=True):
        return

    maya_path = cmds.file(q=True, sn=True)

    # check the file belongs on that project
    correct_project = context_utils.is_file_correct_for_project(maya_path)
    if not correct_project:
        cmds.confirmDialog(title='Incorrect Project',
                           message="File is not of this project environment!\n"
                                   "Restart Maya under the correct project.")
        return

    ctx = context_utils.get_context_from_path(maya_path)
    update_maya_context(ctx)


def update_maya_context(ctx):
    # type: (context.Context) -> None
    """
    Update the context buttons from a given context

    Args:
        ctx (context.Context): Class of data to set to
    """
    def set_button(variable_name, value):
        # type: (str, str) -> None
        """
        Set the button text

        Args:
            variable_name: Name of the environment variable
            value: Value of the environment variable
        """
        btn_name = f"btn_{variable_name}"
        ctx_btn.set_btn_text(variable_name, btn_name, value)

    ctx_btn = context_buttons.ContextButtons()
    set_button("entity", ctx.entity)

    if ctx.is_build:
        # asset name button
        ctx_btn.asset_names_btn()
        set_button("asset_build_name", ctx.asset_build)

        # task button
        ctx_btn.asset_task_btn(ctx.asset_build)
        ctx_btn.set_shot_task(ctx.task)
    else:
        if ctx.episode:
            ctx_btn.episode_list_btn()
            set_button("episode_name", ctx.episode)

        # sequence button
        ctx_btn.sequence_list_btn()
        set_button("sequence_name", ctx.sequence)

        # sequence button
        ctx_btn.shot_list_btn(ctx.sequence)
        set_button("shot_name", ctx.shot)

        # task button
        ctx_btn.shot_task_btn(ctx.shot)
        ctx_btn.set_shot_task(ctx.task)
