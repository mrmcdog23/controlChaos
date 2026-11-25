"""
Maya importer for the JSON written by ue_export_cameras_json.py

Run in Maya's Script Editor (Python tab). Edit JSON_PATH first.
Converts Unreal (left-handed, Z-up, +X forward, cm) to Maya (right-handed, Y-up, -Z forward).
"""
import json
import math
import maya.api.OpenMaya as om
import maya.cmds as cmds
import cccore.utils.file_utils as file_utils

# ----------------------------------------------------------------- settings
JSON_PATH = r"C:/Users/joele/Downloads/ue_cameras.json"   # change me
SCALE = 1.0                               # 1.0 if Maya units are cm; 0.01 for metres
SET_TIMELINE = True
# ---------------------------------------------------------------------------

FPS_NAMES = {24: "film", 25: "pal", 30: "ntsc", 48: "show", 50: "palf", 60: "ntscf"}


def ue_to_maya_vec(v):
    """UE (x fwd, y right, z up) -> Maya (x right, y up, z back)."""
    return om.MVector(v[1], v[2], -v[0])


def build_matrix(frame):
    right = ue_to_maya_vec(frame["right"])
    up = ue_to_maya_vec(frame["up"])
    fwd = ue_to_maya_vec(frame["forward"])
    zaxis = -fwd  # Maya cameras look down -Z
    pos = ue_to_maya_vec(frame["location"]) * SCALE
    return om.MMatrix([
        right.x, right.y, right.z, 0.0,
        up.x, up.y, up.z, 0.0,
        zaxis.x, zaxis.y, zaxis.z, 0.0,
        pos.x, pos.y, pos.z, 1.0,
    ])


def key(node, attr, frame, value):
    cmds.setKeyframe(node, attribute=attr, time=frame, value=value)


def import_camera(json_path, master_camera_path, namespace):
    # type: (str, str, str) -> None
    """
    Import the camera into maya from a json file

    Args:
        json_path: The json file to read the data from
        master_camera_path: The publish camera asset
        namespace: the namespace to use on the asset
    """
    cmds.file(
        master_camera_path,
        namespace=namespace,
        reference=True
    )
    data = file_utils.read_file(json_path)

    xform = f"{namespace}:camera"
    shape = f"{namespace}:cameraShape"
    frames = data["frames"]
    is_cine = data.get("is_cine", True)

    cmds.setAttr(shape + ".filmFit", 1)  # horizontal, matches UE sensor-width behaviour

    prev_rot = None
    prev_lens = {}

    for f in frames:
        t = f["frame"]
        tm = om.MTransformationMatrix(build_matrix(f))
        rot = tm.rotation(asQuaternion=False)
        if prev_rot is not None:
            rot = rot.closestSolution(prev_rot)  # avoid Euler flips
        prev_rot = rot
        pos = tm.translation(om.MSpace.kWorld)

        key(xform, "translateX", t, pos.x)
        key(xform, "translateY", t, pos.y)
        key(xform, "translateZ", t, pos.z)
        key(xform, "rotateX", t, math.degrees(rot.x))
        key(xform, "rotateY", t, math.degrees(rot.y))
        key(xform, "rotateZ", t, math.degrees(rot.z))

        if is_cine:
            lens = {
                "focalLength": f["focal_length"],
                "horizontalFilmAperture": f["sensor_width"] / 25.4,   # mm -> inches
                "verticalFilmAperture": f["sensor_height"] / 25.4,
                "fStop": f["aperture"],
                "focusDistance": f["focus_distance"] * SCALE,
            }
            for attr, val in lens.items():
                # only key when the value changes, to keep curves light
                if prev_lens.get(attr) is None or abs(prev_lens[attr] - val) > 1e-5:
                    key(shape, attr, t, val)
                    prev_lens[attr] = val
        else:
            # plain CameraActor: only horizontal FOV is available
            fov = f["fov"]
            if prev_lens.get("fov") is None or abs(prev_lens["fov"] - fov) > 1e-5:
                haperture = cmds.getAttr(shape + ".horizontalFilmAperture") * 25.4
                focal = (haperture * 0.5) / math.tan(math.radians(fov) * 0.5)
                key(shape, "focalLength", t, focal)
                prev_lens["fov"] = fov

    # Clean up any remaining Euler discontinuities
    cmds.filterCurve(xform + ".rotateX", xform + ".rotateY", xform + ".rotateZ", filter="euler")
