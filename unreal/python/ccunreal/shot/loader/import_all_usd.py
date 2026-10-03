import unreal as ue
import cccore.utils.file_utils as file_utils


def import_all_usd_as_stage(usd_path):
    # type: (str) -> None
    """
    Import a usd file as a stage file in ue

    Args:
        usd_path: The path to the usd file to import
    """
    # Spawn a USD Stage Actor in the current level
    actor_subsystem = ue.get_editor_subsystem(ue.EditorActorSubsystem)
    stage_actor = actor_subsystem.spawn_actor_from_class(
        ue.UsdStageActor, ue.Vector(0, 0, 0)
    )
    
    # Point it at the USD file (this opens the stage)
    stage_actor.set_editor_property("root_layer", ue.FilePath(usd_path))
    
    # Optional: set the time code for animated USD
    stage_actor.set_editor_property("time", 0.0)
    actor_label = file_utils.get_file_name(usd_path)
    stage_actor.set_actor_label(actor_label)
    
    # Get the level sequence the stage actor generated
    sequence = stage_actor.get_level_sequence()
    
    if sequence:
        ue.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
    else:
        print("No level sequence: the stage may have no animation/time samples.")

    ue.LevelSequenceEditorBlueprintLibrary.set_lock_camera_cut_to_viewport(True)
    ue.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()

    camera = get_usd_actor()
    comp = camera.get_cine_camera_component()
    focus = comp.get_editor_property("focus_settings")  # returns a copy of the struct
    focus.focus_method = ue.CameraFocusMethod.DISABLE


def find_cine_camera(actor):
    """Depth-first search through attached actors for the first CineCameraActor."""
    for child in actor.get_attached_actors():
        if isinstance(child, ue.CineCameraActor):
            return child
        found = find_cine_camera(child)
        if found:
            return found
    return None


def get_usd_actor():
    actor_sub = ue.get_editor_subsystem(ue.EditorActorSubsystem)
    for actor in actor_sub.get_all_level_actors():
        if isinstance(actor, ue.UsdStageActor):
            camera = find_cine_camera(actor)
            if camera:
                ue.log_warning(f"{camera}")
                return camera
    return None

