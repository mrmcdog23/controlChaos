""" wrapper for unreal api functions using the subsystem """
import unreal as ue
from typing import Optional


def _get_unreal_editor_subsystem():
    # type: () -> ue.UnrealEditorSubsystem
    """ Returns the unreal editor subsystem """
    return ue.get_editor_subsystem(ue.UnrealEditorSubsystem)


def _get_editor_actor_subsystem():
    # type: () -> ue.EditorActorSubsystem
    """ Returns the unreal editor actor subsystem """
    return ue.get_editor_subsystem(ue.EditorActorSubsystem)


def _get_level_editor_subsystem():
    # type: () -> ue.LevelEditorSubsystem
    """ Returns the level editor subsystem """
    return ue.get_editor_subsystem(ue.LevelEditorSubsystem)


def _get_editor_asset_subsystem():
    # type: () -> ue.EditorAssetSubsystem
    """ Returns the unreal editor asset subsystem """
    return ue.get_editor_subsystem(ue.EditorAssetSubsystem)


def _get_asset_editor_subsystem():
    # type: () -> ue.AssetEditorSubsystem
    """ Returns the unreal asset editor subsystem """
    return ue.get_editor_subsystem(ue.AssetEditorSubsystem)


def _get_level_sequence_editor_subsystem():
    # type: () -> ue.LevelSequenceEditorSubsystem
    """ Returns the level sequence editor subsystem """
    return ue.get_editor_subsystem(ue.LevelSequenceEditorSubsystem)


def _get_movie_pipeline_queue_subsystem():
    # type: () -> ue.MoviePipelineQueueSubsystem
    """ Returns the movie pipeline queue subsystem """
    return ue.get_editor_subsystem(ue.MoviePipelineQueueSubsystem)


def new_level(asset_path):
    # type: (str) -> bool
    """ Create a new level at the supplied asset_path """
    subsys = _get_level_editor_subsystem()
    return subsys.new_level(asset_path)


def load_level(asset_path):
    # type: (str) -> bool
    """ load the level into the given asset path """
    subsys = _get_level_editor_subsystem()
    return subsys.load_level(asset_path)


def save_all_dirty_levels():
    # type: () -> bool
    """ saves all dirty levels """
    subsys = _get_level_editor_subsystem()
    return subsys.save_all_dirty_levels()


def save_current_level():
    # type: () -> bool
    """ Saves the currently opened level """
    subsys = _get_level_editor_subsystem()
    return subsys.save_current_level()


def editor_set_game_view(game_view, viewport_config_key='None'):
    # type: (bool, ue.Name) -> None
    """sets the editor game view (I have no idea)"""
    subsys = _get_level_editor_subsystem()
    return subsys.editor_set_game_view(game_view, viewport_config_key)


def get_pilot_level_actor(viewport_config_key='None'):
    # type: (ue.Name) -> Optional[ue.Actor]
    """gets the currently piloted level actor"""
    subsys = _get_level_editor_subsystem()
    return subsys.get_pilot_level_actor(viewport_config_key)


def get_active_viewport_config_key():
    # type: () -> ue.Name
    """ Returns the active viewport config key """
    subsys = _get_level_editor_subsystem()
    return subsys.get_active_viewport_config_key()


def pilot_level_actor(actor_to_pilot, viewport_config_key='None'):
    # type: (ue.Actor, ue.Name) -> None
    """ pilots the level actor """
    subsys = _get_level_editor_subsystem()
    return subsys.pilot_level_actor(actor_to_pilot, viewport_config_key)


def eject_pilot_level_actor(viewport_config_key='None'):
    # type: (ue.Actor) -> None
    """ eject the pilot the level actor """
    subsys = _get_level_editor_subsystem()
    return subsys.eject_pilot_level_actor(viewport_config_key)


def is_in_play_in_editor():
    # type: () -> bool
    """ Is the editor in play mode """
    subsys = _get_level_editor_subsystem()
    return subsys.is_in_play_in_editor()


def editor_request_end_play():
    # type: () -> None
    """ Requests the editor to end play """
    subsys = _get_level_editor_subsystem()
    return subsys.editor_request_end_play()


def get_editor_world():
    # type: () -> ue.World
    """ Returns the current editor world """
    subsys = _get_unreal_editor_subsystem()
    return subsys.get_editor_world()


def get_game_world():
    # type: () -> ue.World
    """ Returns the current game editor """
    subsys = _get_unreal_editor_subsystem()
    return subsys.get_game_world()


def get_level_viewport_camera_info():
    # type: () -> tuple[ue.Vector, ue.Rotator]
    """ Returns the level viewport camera info """
    subsys = _get_unreal_editor_subsystem()
    return subsys.get_level_viewport_camera_info()


def set_level_viewport_camera_info(camera_location, camera_rotation):
    # type: (ue.Vector, ue.Rotator) -> None
    """ sets the level viewport camera info """
    subsys = _get_unreal_editor_subsystem()
    return subsys.set_level_viewport_camera_info(camera_location, camera_rotation)


def get_all_level_actors():
    # type: () -> ue.Array[ue.Actor]
    """ Returns all actors in the currently open level """
    subsys = _get_editor_actor_subsystem()
    return subsys.get_all_level_actors()


def get_selected_level_actors():
    # type: () -> ue.Array[ue.Actor]
    """ Returns all selected actors in the current level """
    subsys = _get_editor_actor_subsystem()
    return subsys.get_selected_level_actors()


def set_selected_level_actors(actors):
    # type: (ue.Actor) -> None
    """ selects the passed level actors """
    subsys = _get_editor_actor_subsystem()
    subsys.set_selected_level_actors([actor for actor in actors])


def destroy_actor(actor):
    # type: (ue.Actor) -> bool
    """ destroys the actor passed """
    subsys = _get_editor_actor_subsystem()
    return subsys.destroy_actor(actor)


def destroy_actors(actors):
    # type: (ue.Actor) -> bool
    """ destroys the actors passed """
    subsys = _get_editor_actor_subsystem()
    return subsys.destroy_actors(actors)


def spawn_actor_from_object(object_, location, rotation=None, transient=False):
    # type: (ue.Object, ue.Vector, Optional[ue.Rotator], Optional[bool]) -> ue.Actor
    """spawns an actor from the given object, setting the transform as specified"""
    rotation = rotation or (0.0, 0.0, 0.0)
    subsys = _get_editor_actor_subsystem()
    return subsys.spawn_actor_from_object(object_, location, rotation, transient)


def spawn_actor_from_class(actor_class, location, rotation=None, transient=False):
    # type: (ue.Class, ue.Vector, ue.Rotator, bool) -> ue.Actor
    """
    Spawns an actor from the given object.
    Setting the transform as specified
    """
    rotation = rotation or (0.0, 0.0, 0.0)
    subsys = _get_editor_actor_subsystem()
    return subsys.spawn_actor_from_class(actor_class, location, rotation, transient)


def clear_actor_selection_set():
    # type: () -> None
    """ clears the current actor selection """
    subsys = _get_editor_actor_subsystem()
    return subsys.clear_actor_selection_set()


def convert_actors(actors, actor_class, static_mesh_package_path):
    # type: (ue.Actor, ue.Class, str) -> ue.Array[ue.Actor]
    """
    Replaces the supplied actors with actors of the specified class
    """
    subsys = _get_editor_actor_subsystem()
    return subsys.convert_actors([actor for actor in actors], actor_class, static_mesh_package_path)


def duplicate_actor(
    actor,  # type: ue.Actor
    to_world=None,  # type: Optional[ue.World]
    location_offset=(0.0, 0.0, 0.0),  # type: ue.Vector
):
    # type: (...) -> ue.Actor
    """duplicates the given actor"""
    subsys = _get_editor_actor_subsystem()
    return subsys.duplicate_actor(actor, to_world, location_offset)
# endregion


# region editor asset api
def duplicate_asset(src_path, dst_path):
    # type: (str, str) -> Optional[ue.Object]
    """
    duplicates the asset at the given source
    path and copies it to the destination path
    """
    subsys = _get_editor_asset_subsystem()
    return subsys.duplicate_asset(src_path, dst_path)


def duplicate_loaded_asset(src: ue.Object, dst_path: str) -> ue.Object:
    """ duplicates the loaded asset to the destination path
    """
    subsys = _get_editor_asset_subsystem()
    return subsys.duplicate_loaded_asset(src, dst_path)


def rename_asset(asset_path, new_path):
    # type: (str, str) -> bool
    """ renames the asset at the passed path to the new path """
    subsys = _get_editor_asset_subsystem()
    return subsys.rename_asset(asset_path, new_path)


def rename_loaded_asset(asset, new_path):
    # type: (ue.Object, str) -> bool
    """renames the loaded asset, re-pathing it to the new path supplied
    """
    subsys = _get_editor_asset_subsystem()
    return subsys.rename_loaded_asset(asset, new_path)


def save_loaded_asset(asset, only_if_is_dirty=True):
    # type: (ue.Object, bool) -> bool
    """saves the loaded asset"""
    subsys = _get_editor_asset_subsystem()
    return subsys.save_loaded_asset(asset, only_if_is_dirty)


def save_loaded_assets(assets, only_if_is_dirty=True):
    # type: (list[ue.Object], bool) -> bool
    """saves the loaded asset"""
    subsys = _get_editor_asset_subsystem()
    return subsys.save_loaded_assets(assets, only_if_is_dirty)


def save_asset(asset_to_save, only_if_is_dirty=True):
    # type: (str, bool) -> bool
    """
    Save the packages the assets live in. All objects that
    live in the package will be saved. Will try to check out
    the file first.
    """
    subsys = _get_editor_asset_subsystem()
    return subsys.save_asset(asset_to_save, only_if_is_dirty)


def make_directory(directory_path):
    # type: (str) -> bool
    """ Create a directory on disk. """
    subsys = _get_editor_asset_subsystem()
    return subsys.make_directory(directory_path)


def list_assets(directory_path, recursive=True, include_folder=False):
    # type: (str, bool, bool) -> list[str]
    """ Returns a list of assets in a specified directory """
    subsys = _get_editor_asset_subsystem()
    return list(subsys.list_assets(directory_path, recursive, include_folder))


def load_blueprint_class(asset_path):
    # type: (str) -> ue.Class
    """ Load the blueprint into the class """
    return _get_editor_asset_subsystem().load_blueprint_class(asset_path)


def remove_metadata_tag(object_, tag):
    # type: (ue.Object, str) -> None
    """removes the specified metadata tag from the asset"""
    subsys = _get_editor_asset_subsystem()
    return subsys.remove_metadata_tag(object_, tag)


def set_metadata_tag(object_, tag, value):
    # type: (ue.Object, str, str) -> None
    """ sets the specified metadata tag on the asset """
    subsys = _get_editor_asset_subsystem()
    return subsys.set_metadata_tag(object_, tag, value)


def get_tag_values(asset_path):
    # type: (str) -> dict[str, str]
    """ gets the values of the specified tag on the asset """
    subsys = _get_editor_asset_subsystem()
    return dict(subsys.get_tag_values(asset_path))


def get_metadata_tag_values(asset):
    # type: (ue.Object) -> dict
    """ Get the metadata tag values """
    subsys = _get_editor_asset_subsystem()
    return subsys.get_metadata_tag_values(asset)


def delete_asset(asset_path):
    # type: (str) -> bool
    """
    deletes the asset at the path supplied.
    This is a force delete sans reference checks
    """
    subsys = _get_editor_asset_subsystem()
    return subsys.delete_asset(asset_path)


def does_asset_exist(path):
    # type: (str) -> bool
    """ Check the asset exists """
    subsys = _get_editor_asset_subsystem()
    return subsys.does_asset_exist(path)


def get_pie_worlds(include_dedicated_server):
    # type: (bool) -> ue.Array[ue.World]
    """
    Gets the available play in editor
    worlds from the level editor
    """
    return ue.EditorLevelLibrary.get_pie_worlds(include_dedicated_server)


def get_selected_asset_data():
    # type: () -> list[ue.AssetData]
    """
    Gets the asset data for the currently
    selected assets in the content browser.
    """
    return [data for data in ue.EditorUtilityLibrary.get_selected_asset_data()]


def sync_browser_to_objects(assets):
    # type: (list[ue.Object]) -> None
    """ Sync the assets to the content browser """
    return ue.EditorAssetLibrary.sync_browser_to_objects(assets)


def open_editor_for_assets(assets):
    # type: (list[ue.Object]) -> None
    """ Open the asset the editor """
    subsys = _get_asset_editor_subsystem()
    subsys.open_editor_for_assets(assets)


def convert_to_spawnable(object_binding):
    # type: (ue.MovieSceneBindingProxy) -> list[ue.MovieSceneBindingProxy]
    """
    Convert an object binding to spawnable. If there are multiple
    objects assigned to the possessable, multiple spawnables will be created.
    """
    subsys = _get_level_sequence_editor_subsystem()
    return list(subsys.convert_to_spawnable(object_binding))


def convert_to_possessable(object_binding):
    # type: (ue.MovieSceneBindingProxy) -> None
    """
    Convert an object binding to possessable. If there are multiple
    objects assigned to the spawnable, multiple spawnables will be created.
    """
    subsys = _get_level_sequence_editor_subsystem()
    subsys.convert_to_possessable(object_binding)


def fix_bindings() -> None:
    """
    Fix the bindings in the currently opened sequence
    """
    subsys = _get_level_sequence_editor_subsystem()
    subsys.fix_actor_references()


def get_current_level_sequence():
    # type: () -> ue.LevelSequence
    """ Get the current level sequence """
    return ue.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()


def add_actors_to_current_sequence(actors):
    # type: (list[ue.Actor]) -> None
    """ Add actors to the current level sequence """
    subsys = _get_level_sequence_editor_subsystem()
    subsys.add_actors(actors)


def get_queue():
    # type: () -> ue.MoviePipelineQueue
    """ Get the movie pipeline queue """
    return _get_movie_pipeline_queue_subsystem().get_queue()


def render_queue_with_executor_instance(executor):
    # type: (ue.MoviePipelineExecutorBase) -> None
    """ Renders the queue using the executor instance """
    _get_movie_pipeline_queue_subsystem().render_queue_with_executor_instance(executor)


def get_texture_parameter_names(mat_inf):
    # type: (ue.MaterialInterface) -> list[ue.Name]
    """ Get the texture parameter names """
    return [name for name in ue.MaterialEditingLibrary.get_texture_parameter_names(mat_inf)]


def get_texture_parameter_source(mat_inf, param_name):
    # type: (ue.MaterialInterface, ue.Name) -> ue.SoftObjectPath
    """ Get the texture parameter source """
    return ue.MaterialEditingLibrary.get_texture_parameter_source(
        mat_inf, param_name)


def get_material_instance_texture_parameter_value(instance, parameter_name, association):
    # type: (ue.MaterialInstance, ue.Name, ue.MaterialParameterAssociation) -> ue.Texture
    """ Get the material instance texture parameter """
    return ue.MaterialEditingLibrary.get_material_instance_texture_parameter_value(
            instance, parameter_name, association)


def get_material_default_texture_parameter_value(mat, param_name):
    # type: (ue.Material, ue.Name) -> ue.Texture
    """ Get the material instance texture parameter value """
    return ue.MaterialEditingLibrary.get_material_default_texture_parameter_value(
        mat, param_name)


def set_material_instance_texture_parameter_value(instance, parameter_name, value, association):
    # type: (ue.MaterialInstanceConstant, ue.Name, ue.Texture, ue.MaterialParameterAssociation) -> bool
    """ Set the material instance texture parameter value """
    return ue.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
        instance, parameter_name, value, association)


def get_used_textures(material):
    # type: (ue.Material) -> list[ue.Texture]
    """ The used textures on a material """
    return list(ue.MaterialEditingLibrary.get_used_textures(material))


def _get_skeletal_mesh_editor_subsys():
    # type: () -> ue.SkeletalMeshEditorSubsystem
    """ Get skeletal mesh subsystem """
    return ue.get_editor_subsystem(ue.SkeletalMeshEditorSubsystem)


def create_physics_asset(skm):
    # type: (ue.SkeletalMesh) -> ue.PhysicsAsset
    """ Create a physics asset """
    subsys = _get_skeletal_mesh_editor_subsys()
    return subsys.create_physics_asset(skm)


def compile_blueprint(blueprint):
    # type: (ue.Blueprint) -> None
    """ Compile a blueprint """
    return ue.BlueprintEditorLibrary.compile_blueprint(blueprint)


def load_map(path):
    # type: (str) -> ue.World
    """ Load a map into the editor """
    return ue.EditorLoadingAndSavingUtils.load_map(path)


def copy_bindings(bindings):
    # type: (list[ue.MovieSceneBindingProxy]) -> str
    """ Add bindings to unreal clipboard. """
    return _get_level_sequence_editor_subsystem().copy_bindings(bindings)


def paste_bindings(text_to_import, paste_bindings_params):
    # type: (str, ue.MovieScenePasteBindingsParam) -> Optional[list[ue.MovieSceneBindingProxy]]
    """
    Paste bindings from unreal clipboard based on the
    configuration of the provided
    """
    result = _get_level_sequence_editor_subsystem().paste_bindings(
        text_to_import, paste_bindings_params
    )
    return list(result) if result is not None else None


def copy_tracks(tracks):
    # type: (list[ue.MovieSceneTrack]) -> str
    """  Add tracks to unreal clipboard """
    return _get_level_sequence_editor_subsystem().copy_tracks(tracks)


def paste_tracks(text_to_import, paste_bindings_params):
    # type: (str, ue.MovieScenePasteTracksParams) -> Optional[list[ue.MovieSceneTrack]]
    """
    Paste tracks from the clipboard based on the configuration of the provided
    """
    result = _get_level_sequence_editor_subsystem().paste_tracks(
        text_to_import, paste_bindings_params
    )
    return list(result) if result is not None else None


def copy_sections(sections):
    # type: (list[ue.MovieSceneSection]) -> str
    """ Add sections to unreal clipboard. """
    return _get_level_sequence_editor_subsystem().copy_sections(sections)


def paste_sections(text_to_import, paste_bindings_params):
    # type: (str, ue.MovieScenePasteSectionsParams) -> Optional[list[ue.MovieSceneSection]]
    """
    Paste sections from unreal clipboard based on the
    configuration of the provided
    """
    result = _get_level_sequence_editor_subsystem().paste_sections(
        text_to_import, paste_bindings_params
    )
    return list(result) if result is not None else None


def add_actors_to_binding(actors, binding):
    # type: (ue.Array[ue.Actor], ue.MovieSceneBindingProxy) -> None
    """ Add actors to the sequence bindings """
    subsys = _get_level_sequence_editor_subsystem()
    subsys.add_actors_to_binding(actors, binding)

