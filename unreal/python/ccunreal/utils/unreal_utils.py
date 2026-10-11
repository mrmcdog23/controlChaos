""" Utilities relating to Unreal """
import sys
import unreal as ue
from CCPySide import QtWidgets, QUiLoader
from typing import Optional
import ccunreal.utils.api_wrap as api_wrap
import ccunreal.utils.unreal_context as unreal_context


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



def actor_type_on_level(actor_type):
    # type: (str) -> Optional[ue.Object]
    """
    Check an actor of particular type exists on a level

    Args:
        actor_type: Actor type to find

    Returns:
        actor: The actor that matches the type
    """
    actors = ue.GameplayStatics.get_all_actors_of_class(
        ue.EditorLevelLibrary.get_editor_world(), ue.CineCameraActor
    )
    for actor in actors:
        if isinstance(actor, actor_type):
            return actor


def spawn_actor_if_not_exists(actor_type):
    # type: (Any) -> ue.Object
    """
    Spawn an actor of a class only if it doesnt exists already

    Args:
        actor_type: Object class to create

    Returns:
        Found or created object
    """
    actor = actor_type_on_level(actor_type)
    if actor:
        return actor
    actor = api_wrap.spawn_actor_from_object(actor_type())
    ue.log(f"Created actor: {actor}")
    return actor


def fbx_from_actor_tag(actor):
    # type: (ue.Actor) -> str
    """
    get the fbx path from and actor

    Args:
        actor: The actor to check

    Returns:
        path of the fbx
    """
    try:
        return actor.tags[0]
    except IndexError:
        return str()


def create_sky_and_lights():
    """
    Create sky atmosphere and direct light
    """
    # create atmosphere and cloud
    spawn_actor_if_not_exists(ue.SkyAtmosphere)
    spawn_actor_if_not_exists(ue.VolumetricCloud)

    # create directional light
    direct_light_actor = spawn_actor_if_not_exists(ue.DirectionalLight)
    rot = ue.Rotator(0, -20, -40.0)
    direct_light_actor.set_actor_rotation(rot, False)
    direct_light_actor.light_component.set_editor_property("Intensity", 3)

    # create point light
    point_light_actor = spawn_actor_if_not_exists(ue.PointLight)
    point_light_location = ue.Vector(130, -140, 250)
    point_light_actor.set_actor_location(point_light_location, False, False)
    point_light_actor.light_component.set_editor_property("Intensity", 3)

    # create cloud
    spawn_actor_if_not_exists(ue.VolumetricCloud)


def list_subfolders(folder_path, recursive=False):
    # type: (str, Optional[bool]) ->  list[str]
    """
    Within unreal list the subfolders from the current folder

    Args:
        folder_path: Unreal folder path to check subfolders
        recursive: Whether to check the immediate subfolders
    """
    asset_registry = ue.AssetRegistryHelpers.get_asset_registry()
    if not ue.EditorAssetLibrary.does_directory_exist(folder_path):
        ue.log_warning(f"Folder not found: {folder_path}")
        return list()

    subfolders = asset_registry.get_sub_paths(folder_path, recursive)
    folder_names = list()
    for folder_path in subfolders:
        base_name = ue.Paths.get_base_filename(folder_path)
        folder_names.append(base_name)  # "SubFolder"
    return folder_names


def get_asset_from_path(file_path, folder_root=None):
    """
    From a file path find the asset in the project

    Args:
        file_path: Path to the file to find
    """
    asset_registry = ue.AssetRegistryHelpers.get_asset_registry()
    folder_root = folder_root or "/Game"
    # Get all assets under /Game
    filter = ue.ARFilter(
        class_names=["StaticMesh", "SkeletalMesh"],
        package_paths=[folder_root],
        recursive_paths=True,
        recursive_classes=True
    )
    assets = asset_registry.get_assets(filter)
    for asset in assets:
        loaded_asset = ue.EditorAssetLibrary.load_asset(asset.package_name)
        asset_import_data = loaded_asset.get_editor_property('asset_import_data')
        first_filename = asset_import_data.get_first_filename()
        if file_path == first_filename:
            return loaded_asset


def find_all_assets_of_type(directory, find_asset_type):
    # type: (str, str) -> list[ue.Object]
    """
    Get all assets of a specific type in a directory

    Args:
        directory: The folder to look for the asset
        find_asset_type: Asset type to find

    Returns:
        all_assets_of_type: List of assets found
    """
    all_assets_of_type = list()
    path_to_type = get_path_to_type_dict(directory)
    for object_path, asset_type in path_to_type.items():
        if asset_type == find_asset_type:
            asset = ue.load_asset(object_path)
            all_assets_of_type.append(asset)
    return all_assets_of_type


def find_asset_of_type(directory, find_asset_type, assets_before=None):
    # type: (str, str, Optional[ue.Object]) -> Optional[ue.Object]
    """
    Get an asset of a specific type in a directory

    Args:
        directory: The folder to look for the asset
        find_asset_type: Asset type to find
        assets_before: List of already found assets

    Returns:
        asset: The loaded asset found
    """
    all_assets_of_type = find_all_assets_of_type(directory, find_asset_type)
    if assets_before and all_assets_of_type:
        for asset in all_assets_of_type:
            if asset not in assets_before:
                return asset

    if all_assets_of_type:
        return all_assets_of_type[0]


def current_map_path():
    # type: () -> str
    """ Get the current open map path """
    return api_wrap.get_editor_world().get_path_name()


def current_ls_path():
    # type: () -> Optional[str]
    """ Get the current open level sequence path """
    current_sequence = api_wrap.get_current_level_sequence()
    if current_sequence:
        return current_sequence.get_path_name()


def context_dict_from_path(asset_path):
    # type: (str) -> dict
    """
    From a file path work out the context dictionary

    Args:
        asset_path: Path of the file to work out

    Returns:
        context_dict: Dictionary of the context
    """
    # set the root of the project
    path_split = asset_path.split("/")
    print (path_split)
    context_dict = {"entity": "shot", "task_name": "previz"}
    if len(path_split) == 7:
        context_dict["episode_name"] = path_split[3]
        context_dict["sequence_name"] = path_split[4]
        context_dict["shot_name"] = path_split[5]
    else:
        context_dict["sequence_name"] = path_split[3]
        context_dict["shot_name"] = path_split[4]
    return context_dict


def get_context_from_path(asset_path):
    # type: (str) -> unreal_context.UnrealContext
    """
    From the level sequence path get the shot context
    class by reading the metadata values

    Args:
        asset_path: Asset sequence path

    Returns:
        ctx: Set context class
    """
    overrides = context_dict_from_path(asset_path)
    ctx = unreal_context.UnrealContext(overrides=overrides)
    return ctx


def apply_metadata(metadata_dict, asset, save=False):
    # type: (dict, ue.Object, bool) -> None
    """
    Using the asset version class and is values

    Args:
        metadata_dict: No8 data to add
        asset: The unreal asset to add metadata to
        save: If True save the asset
    """
    for key, value in metadata_dict.items():
        add_metadata_value(asset, key, value)
    if save:
        api_wrap.save_asset(asset.get_full_name())


def add_metadata_value(asset, key, value, add_no_prefix=True):
    # type: (ue.Object, str, str, Optional[bool]) -> None
    """
    Add the metadata values to the asset

    Args:
        asset: The unreal asset to add metadata to
        key: Dictionary context key to add
        value: Value of the context
        add_no_prefix: Add a prefix to the tag
    """
    if not add_no_prefix:
        api_wrap.set_metadata_tag(asset, key, str(value))
    else:
        no8_key = f"{unreal_constants.NO8_METADATA_PREFIX}.{key}"
        api_wrap.set_metadata_tag(asset, no8_key, str(value))
    api_wrap.save_asset(asset.get_full_name())