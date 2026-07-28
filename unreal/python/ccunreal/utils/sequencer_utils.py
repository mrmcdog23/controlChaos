""" Utilities relating to the unreal level sequencer """
import os
import unreal as ue
from typing import Optional
import cccore.utils.file_utils as file_utils


def _sequencer_lib():
    """
    Need a shortcut to this long name library, but don't want
    to store at module scope b/c this causes issues at Editor shutdown.
    """
    return ue.LevelSequenceEditorBlueprintLibrary


def find_binding_by_display_name(name, sequence):
    # type: (str, ue.LevelSequence) -> Optional[ue.SequencerBindingProxy]
    """
    Find a binding from its display name

    Args:
        name: Binding name to search for
        sequence: Level sequence to search in for binding

    Returns:
        binding: The binding found matching the name
    """
    #binding = ue_no8.find_binding_by_display_name(name, sequence)
    #if binding.get_name():
    #    return binding
    return


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


def find_sequence_actor(sequence, actor):
    # type: (ue.Object, Optional[ue.Actor]) -> ue.Actor
    """
    The shot will only have one camera binding
    so look for it on the level sequence

    Args:
        sequence: Level sequence to search in for binding
        actor: Actor instance to find

    Returns:
        binding: The cameras sequence binding
    """
    for binding in sequence.get_bindings():
        binding_id = sequence.get_portable_binding_id(sequence, binding)
        bound_actors = ue.LevelSequenceEditorBlueprintLibrary.get_bound_objects(binding_id)
        for bound_actor in bound_actors:
            # if the actor matches the bound actor return
            if actor and actor == bound_actor:
                return actor


def setup_transform_track(binding):
    # type: (ue.SequencerBindingProxy) -> (ue.MovieScene3DTransformTrack, ue.MovieScene3DTransformSection)
    """
    Add a track in a level sequence and add a section

    Args:
        binding: The binding to add the track to

    Returns:
        track: The newly created track
        section: The new section on the sequencer
    """
    track = binding.add_track(ue.MovieScene3DTransformTrack)
    section = track.add_section()
    set_section_range(section)
    return track, section


def set_section_range(section, start_frame=None, end_frame=None):
    # type: (ue.Section, Optional[int], Optional[int]) -> None
    """
    Sets the frame range on a sequencer Section.

    Args:
        section: The section to set range on
        start_frame: The start frame
        end_frame: The end frame
    """
    ue.log(f"Setting {section} to {start_frame}-{end_frame}")
    if end_frame:
        section.set_end_frame(int(end_frame))
    else:
        section.set_end_frame_bounded(False)
    if start_frame:
        section.set_start_frame_bounded(True)
        section.set_start_frame(int(start_frame))
    else:
        section.set_start_frame_bounded(False)


def get_level_sequence_frame_range(level_sequence):
    # type: (ue.LevelSequence) -> (int, int)
    """
    Get the frame range of the level sequence

    Args:
        level_sequence: Level sequence to find range for

    Returns:
        ls_start_frame: The first frame of the level
        ls_end_frame: The last frame of the level
    """
    track = level_sequence.get_tracks()[0]
    section = track.get_sections()[0]
    ls_start_frame = section.get_start_frame()
    ls_end_frame = section.get_end_frame()
    return ls_start_frame, ls_end_frame


def get_channel_name(channel):
    """
    Get the "name" of the channel. Something changed in 4.26.2, so
    we need to be careful to get it the best way. Through some magic,
    channels in 4.26 have a "channel_name" attr that is not mentioned in
    the API docs.

    Args:
        channel (MovieSceneScriptingChannel):

    Returns:
        str
    """
    try:
        return str(channel.channel_name)
    except AttributeError:
        return channel.get_name()


def set_sequencer_transform_defaults(xform_section, xform):
    """
    Sets transform data on a sequencer transform track.

    Parameters:
    xform_section (ue.MovieScene3DTransformSection): The section to set defaults on
    xform (ue.Transform): The transform data to apply

    """
    channels = xform_section.get_all_channels()

    for channel in channels:
        if get_channel_name(channel) == "Weight":
            continue
        elif get_channel_name(channel) == "Location.X":
            channel.set_default(xform.translation.x)
        elif get_channel_name(channel) == "Location.Y":
            channel.set_default(xform.translation.y)
        elif get_channel_name(channel) == "Location.Z":
            channel.set_default(xform.translation.z)
        elif get_channel_name(channel) == "Rotation.X":
            channel.set_default(xform.rotation.euler().x)
        elif get_channel_name(channel) == "Rotation.Y":
            channel.set_default(xform.rotation.euler().y)
        elif get_channel_name(channel) == "Rotation.Z":
            channel.set_default(xform.rotation.euler().z)
        elif get_channel_name(channel) == "Scale.X":
            channel.set_default(xform.scale3d.x)
        elif get_channel_name(channel) == "Scale.Y":
            channel.set_default(xform.scale3d.y)
        elif get_channel_name(channel) == "Scale.Z":
            channel.set_default(xform.scale3d.z)


def attach_to_binding(src_binding, dst_binding):
    """
    Attach one binding to another

    Args:
        src_binding (ue.SequencerBindingProxy): Source sequencer binding
        dst_binding (ue.SequencerBindingProxy): The sequencer binding to attach to
    """
    track = src_binding.add_track(ue.MovieScene3DAttachTrack)
    section = track.add_section()  # type: ue.MovieScene3DConstraintSection
    section.set_start_frame_bounded(False)
    section.set_end_frame_bounded(False)

    sequence = src_binding.sequence
    id_ = sequence.get_portable_binding_id(sequence, dst_binding)
    section.set_constraint_binding_id(id_)


def open_level_sequence(level_sequence):
    # type: (ue.LevelSequence) -> bool
    """Opens a level sequence in the sequencer."""
    return _sequencer_lib().open_level_sequence(level_sequence)


def set_current_time(new_frame):
    # type: (int) -> None
    """Set the current time/frame in sequencer."""
    _sequencer_lib().set_current_time(new_frame)


def create_level_sequence(ls_path, fps, source_level_sequence=None):
    # type: (str, float, Optional[ue.LevelSequence]) -> ue.LevelSequence
    """
    Create a level sequence from scratch or if a source is given duplicate it

    Args:
        ls_path: Path to create level sequence
        fps: Number of frames per second
        source_level_sequence: If copying give it a source

    Returns:
        ls: The new level sequence
    """
    if ue.EditorAssetLibrary.does_asset_exist(ls_path):
        return ue.load_asset(ls_path)

    asset_name = ue.Paths.get_base_filename(ls_path)
    package_path = ue.Paths.get_path(ls_path)
    asset_tools = ue.AssetToolsHelpers.get_asset_tools()

    if not source_level_sequence:
        ue.log_warning("Creating new level sequence...")
        ls = ue.AssetTools.create_asset(
            asset_tools,
            asset_name=asset_name,
            package_path=package_path,
            asset_class=ue.LevelSequence,
            factory=ue.LevelSequenceFactoryNew()
        )
        # Set the display rate
        frame_rate = ue.FrameRate(numerator=fps, denominator=1)
        ls.set_display_rate(frame_rate)
    else:
        # duplicate level sequence asset
        ue.log_warning("Duplicating level sequence...")
        ls = asset_tools.duplicate_asset(
            asset_name, package_path, source_level_sequence)
    return ls


def set_level_sequence_view_range(sequence, start, end, fps):
    # type: (ue.LevelSequence, float, float, float) -> None
    """
    Set the view which has to be done in seconds

    Args:
        sequence: The level sequence to set
        start: The start frame of the view
        end: The end frame of the view
        fps: Frames per second of the level
    """
    sequence.set_playback_start(start)
    sequence.set_playback_end(end)

    start_in_seconds = float(start - 10) / float(fps)
    end_in_seconds = float(end + 10) / float(fps)
    sequence.set_view_range_start(start_in_seconds)
    sequence.set_view_range_end(end_in_seconds)


def export_fbx_file(fbx_file_path, world, level_sequence, bindings):
    # type: (str, ue.World, ue.LevelSequence,list[ue.MovieSceneBindingProxy]) -> None
    """
    Export fbx file of the actor from the level sequence

    Args:
        fbx_file_path: Path of the fbx to export
        world: Map of the world to export
        level_sequence: Level sequence to export from
        bindings: List of binding on the level sequence
    """
    ue.log_warning(f"FBX Export path: {fbx_file_path}")
    file_utils.create_directories(os.path.dirname(fbx_file_path))

    override_options = ue.FbxExportOption()
    override_options.ascii = False
    override_options.collision = False
    override_options.export_local_time = False
    override_options.export_preview_mesh = True
    override_options.export_source_mesh = False
    override_options.fbx_export_compatibility = ue.FbxExportCompatibility.FBX_2020
    override_options.force_front_x_axis = False
    override_options.level_of_detail = False
    override_options.map_skeletal_motion_to_root = False
    override_options.vertex_color = False

    params = ue.SequencerExportFBXParams(
        world=world,
        sequence=level_sequence,
        root_sequence=level_sequence,
        bindings=bindings,
        override_options=override_options,
        fbx_file_name=fbx_file_path,
    )
    ue.SequencerTools.export_level_sequence_fbx(params)