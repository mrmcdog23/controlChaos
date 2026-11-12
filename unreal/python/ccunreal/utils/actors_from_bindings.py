""" Get an actor from its binding """
import unreal as ue


def get_actor_from_binding(seq, binding):
    # type: (ue.LevelSequence, ue.MovieSceneBindingProxy) -> ue.Actor
    """
    From a level sequence binding get the actor

    Args:
        seq: The level sequence loaded
        binding: The binding on the camera

    Returns:
        The actor found from the binding
    """
    # Component bindings: resolve the parent (the actor) instead
    parent = binding.get_parent()
    if parent.sequence is not None and parent.get_name():
        binding = parent

    objs = []

    # Route 1: via the Sequencer (sequence must be open)
    try:
        ue.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
        bid = ue.MovieSceneSequenceExtensions.get_binding_id(seq, binding)
        objs = ue.LevelSequenceEditorBlueprintLibrary.get_bound_objects(bid)
    except Exception as e:
        print("Route 1 failed:", e)

    # Route 2: locate_bound_objects against the editor world
    if not objs:
        try:
            world = ue.get_editor_subsystem(ue.UnrealEditorSubsystem).get_editor_world()
            objs = ue.MovieSceneSequenceExtensions.locate_bound_objects(seq, binding, world)
        except Exception as e:
            print("Route 2 failed:", e)

    # Route 3: match the binding name to an actor label in the level
    if not objs:
        actors = ue.get_editor_subsystem(ue.EditorActorSubsystem).get_all_level_actors()
        objs = [a for a in actors if a.get_actor_label() == binding.get_name()]

    if not objs:
        return None
    obj = objs[0]
    # If a component came back, return its owning actor
    return obj.get_owner() if isinstance(obj, ue.ActorComponent) else obj
