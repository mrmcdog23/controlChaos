import unreal as ue


def find_binding_by_actor_class(actor_class, sequence):
    # type: (ue.Actor, ue.LevelSequence) -> Optional[ue.SequencerBindingProxy]
    """
    Find a binding from its display name

    Args:
        actor_class: The actor class to find
        sequence: Level sequence to search in for binding

    Returns:
        binding: The binding found matching the name
    """
    for binding in sequence.get_bindings():
        binding_id = sequence.get_portable_binding_id(sequence, binding)
        bound_actors = ue.LevelSequenceEditorBlueprintLibrary.get_bound_objects(binding_id)
        for bound_actor in bound_actors:
            # if there is an actor class and it matches current actor
            if actor_class and isinstance(bound_actor, actor_class):
                return binding


def camera_ue_options():
    # type: () ->  ue.MovieSceneUserImportFBXSettings
    """
    Import camera fbx settings into the level sequence
    """
    import_options = ue.MovieSceneUserImportFBXSettings()
    import_options.set_editor_property('create_cameras', False)
    import_options.set_editor_property('force_front_x_axis', False)
    import_options.set_editor_property('match_by_name_only', False)
    import_options.set_editor_property('reduce_keys', False)
    import_options.set_editor_property('reduce_keys_tolerance', 0.001)
    return import_options
