"""
Unreal -> JSON camera exporter (works with spawnable AND possessable cameras).

Run inside the Unreal Editor (Output Log > Python, or Tools > Execute Python Script)
with the Level Sequence you want to export OPEN in Sequencer.

It steps through the playback range, lets Sequencer spawn/evaluate each camera,
and records world transform + lens data per frame.
"""
import json
import os
import unreal
import cccore.utils.file_utils as file_utils


def vec(v):
    return [v.x, v.y, v.z]


def read_camera_frame(actor, frame):
    """
    Sample one camera actor at the current sequencer time.
    """
    # Sequencer often animates the CAMERA COMPONENT (relative to the actor root),
    # so always read the component's world transform, not the actor's.
    if isinstance(actor, unreal.CineCameraActor):
        comp = actor.get_cine_camera_component()
    else:
        comp = actor.get_editor_property("camera_component")

    loc = comp.get_world_location()
    rot = comp.get_world_rotation()

    data = {
        "frame": frame,
        "location": vec(loc),                                  # cm, UE space
        "rotation": [rot.roll, rot.pitch, rot.yaw],            # degrees, UE space
        "forward": vec(unreal.MathLibrary.get_forward_vector(rot)),
        "right": vec(unreal.MathLibrary.get_right_vector(rot)),
        "up": vec(unreal.MathLibrary.get_up_vector(rot)),
    }

    if isinstance(actor, unreal.CineCameraActor):
        filmback = comp.get_editor_property("filmback")
        data["focal_length"] = comp.get_editor_property("current_focal_length")   # mm
        data["aperture"] = comp.get_editor_property("current_aperture")           # f-stop
        data["focus_distance"] = comp.get_editor_property("current_focus_distance")  # cm
        data["sensor_width"] = filmback.get_editor_property("sensor_width")       # mm
        data["sensor_height"] = filmback.get_editor_property("sensor_height")     # mm
    else:
        data["fov"] = comp.get_editor_property("field_of_view")
        data["aspect_ratio"] = comp.get_editor_property("aspect_ratio")

    return data


def export_camera(json_path, actor_name, sequence_actor, seq):
    # type: (str, str, unreal.Actor, unreal.LevelSequence) -> None
    """
    Export a level sequence camera as a json file and store the settings

    Args:
        json_path: Path of the json file to save
        actor_name: Name of the camera to save
        sequence_actor: Unreal camera to export
        seq: The level sequence the camera is on
    """
    rate = seq.get_display_rate()
    fps = rate.numerator / float(rate.denominator)
    start = int(round(seq.get_playback_start_seconds() * fps))
    end = int(round(seq.get_playback_end_seconds() * fps))

    original_time = unreal.LevelSequenceEditorBlueprintLibrary.get_current_time()

    frames_list = list()

    for frame in range(start, end + 1):
        unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(frame)
        unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()
        frames_list.append(read_camera_frame(sequence_actor, frame))

    # Put the playhead back where the user left it
    unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(original_time)

    data = {
        "source": "unreal",
        "sequence": seq.get_name(),
        "fps": fps,
        "start_frame": start,
        "end_frame": end,
        "units": "cm",
        "frames": frames_list,
        "actor_name": actor_name
    }
    file_utils.create_directories(json_path)
    file_utils.write_file(json_path, data)
    unreal.log(f"Exported camera to {json_path}")

