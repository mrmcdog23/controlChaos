""" Functions to run on Houdini startup """
import hou
import toolutils
import cccore.file_env.context_utils as context_utils
import cchoudini.panel.create_cc_panel as create_cc_panel
import cchoudini.utils.hou_utils as hou_utils
import ccftrack.shot as shot


def set_fps():
    """
    Set the frames per second of the project
    """
    fps = shot.FtShot().fps
    hou.setFps(fps)


def run_setup_modules():
    """
    Create the cc panel on startup
    """
    if not hou.isUIAvailable():
        return
    create_cc_panel.make_context_panel()
    import hdefereval
    hdefereval.executeDeferred(lambda: flipbook_utils.set_flipbook_output())


def register_callbacks(event):
    # type: (hou.hipFileEventType) -> None
    """
    Register all houdini callbacks

    Args:
        event: Event types
    """
    if event in [hou.hipFileEventType.AfterSave, hou.hipFileEventType.AfterLoad]:
        # set the context and houdini variables
        # from the scene path after its loaded
        hip_path = hou.hipFile.path()
        ctx = context_utils.get_context_from_path(hip_path)
        hou_utils.set_houdini_vars_from_ctx(ctx)

    if event == hou.hipFileEventType.AfterClear:
        set_fps()


hou.hipFile.addEventCallback(register_callbacks)

set_fps()
run_setup_modules()

