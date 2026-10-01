import unreal as ue


def import_all_usd_as_stage(usd_path):
    # Spawn a USD Stage Actor in the current level
    actor_subsystem = ue.get_editor_subsystem(ue.EditorActorSubsystem)
    stage_actor = actor_subsystem.spawn_actor_from_class(
        ue.UsdStageActor, ue.Vector(0, 0, 0)
    )
    
    # Point it at the USD file (this opens the stage)
    stage_actor.set_editor_property("root_layer", ue.FilePath(usd_path))
    
    # Optional: set the time code for animated USD
    stage_actor.set_editor_property("time", 0.0)
    
    stage_actor.set_actor_label("MyUsdStage")
    
    # Get the level sequence the stage actor generated
    sequence = stage_actor.get_level_sequence()
    
    if sequence:
        ue.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
    else:
        print("No level sequence: the stage may have no animation/time samples.")