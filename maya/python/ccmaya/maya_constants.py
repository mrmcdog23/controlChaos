TRANSLATE = ["tx", "ty", "tz"]
ROTATE    = ["rx", "ry", "rz"]
SCALE     = ["sx", "sy", "sz"]
VISIBILITY = ["v"]


DEFAULT_CAMERAS = ["persp", "top", "front", "side"]

# Ftrack attribute
FTRACK_ID = "ftrackId"


ROOT_JNT = "root_jnt"
MAIN_CTRL = "main_ctl"

# maya group names
ASSET_GRP = "ASSET"
CAM_GRP = "CAM"
GEO_GRP = "GEO"
RIG_GRP = "RIG"
JNT_GRP = "JNTS"
CTLS_GRP = "CTLS"
GRP_NAMES = [ASSET_GRP, CAM_GRP, GEO_GRP, RIG_GRP]

# alembic arguments
MESH_ABC_ARGS = ["-uvWrite", "-writeVisibility", "-writeUVSets",
                 "-worldSpace", "-dataFormat", "ogawa", "-stripNamespaces"
                 ]
CAM_ABC_ARGS = ["-worldSpace", "-stripNamespaces"]
JOB_ARGS_FORMAT = "-step {step} -fr {start} {end} {args} -root {root} -file {path}"

# frames per second dictionary
FPS = {
    15: "game",
    23.976: "23.976fps",
    24: "film",
    25: "pal",
    29.97: "29.97fps",
    30: "game",
    48: "show",
    50: "palf",
    60: "ntscf"
}
