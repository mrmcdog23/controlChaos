import unreal as ue

""" Utilities relating to Unreal """
import sys
import unreal as ue
from CCPySide import QtWidgets, QUiLoader
from typing import Optional


def launch_unreal_win(win_class):
    # type: (QtWidgets.QMainWindow) -> None
    """
    Launch the unreal window

    Args:
        win_class: Class of ui to open
    """
    # delete all current versions of the tool
    for inst in QtWidgets.QApplication.topLevelWidgets():
        if win_class.title == inst.windowTitle():
            inst.close()
            inst.deleteLater()

    # NOTICE: Initialized before "QApplication"
    # unreal freezes without this
    loader = QUiLoader()
    if not QtWidgets.QApplication.instance():
        QtWidgets.QApplication(sys.argv)
    else:
        QtWidgets.QApplication.instance()

    global window
    window = win_class(None)
    window.show()
    ue.parent_external_window_to_slate(window.winId())


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


def get_path_to_type_dict(directory):
    # type: (str) -> dict
    """
    From a directory loop through all the assets in
    the directory and build a dictionary of an object
    path to its asset type.

    Args:
        directory: Path to the directory to check

    Returns:
        path_to_type: Object path to its type
    """
    path_to_type = dict()
    asset_registry = ue.AssetRegistryHelpers.get_asset_registry()
    object_paths = ue.EditorAssetLibrary.list_assets(directory)
    for object_path in object_paths:
        asset = asset_registry.get_asset_by_object_path(object_path)
        path_to_type[object_path] = asset.get_class().get_fname()
    return path_to_type


def get_object_path(directory, find_asset_type, ignore_paths=None):
    # type: (str, str, Optional[list[str]]) -> Optional[str]
    """
    In a directory get an object path of a type

    Args:
        directory: Unreal directory path to check
        find_asset_type: Match object type
        ignore_paths: List of paths to ignore

    Returns:
        object_path: The found object path
    """
    path_to_type = get_path_to_type_dict(directory)
    for object_path, asset_type in path_to_type.items():
        if ignore_paths and object_path in ignore_paths:
            continue
        if asset_type == find_asset_type:
            return object_path


def get_objects_from_list(object_paths, find_asset_type):
    asset_registry = ue.AssetRegistryHelpers.get_asset_registry()
    for object_path in object_paths:
        asset = asset_registry.get_asset_by_object_path(object_path)
        asset_type = asset.get_class().get_fname()
        if asset_type == find_asset_type:
            return object_path
