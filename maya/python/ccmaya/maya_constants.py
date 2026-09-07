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