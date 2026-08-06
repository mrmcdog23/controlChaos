TRANSLATE = ["tx", "ty", "tz"]
ROTATE    = ["rx", "ry", "rz"]
SCALE     = ["sx", "sy", "sz"]
VISIBILITY = ["v"]


DEFAULT_CAMERAS = ["persp", "top", "front", "side"]
EXPORT_GROUPS = ["GEO", "CAM", "ENV"]
GEO_GRP = "GEO"
CAM_GRP = "CAM"
ENV_GRP = "ENV"
JNT_GRP = "JNT"
RIG_GRP = "RIG"
ROOT_JNT = "root_jnt"
MAIN_CTRL = "main_ctl"
CTLS_GRP = "CTLS"

# alembic arguments
MESH_ABC_ARGS = ["-uvWrite", "-writeVisibility", "-writeUVSets",
                 "-worldSpace", "-dataFormat", "ogawa", "-stripNamespaces"
                 ]
CAM_ABC_ARGS = ["-worldSpace", "-stripNamespaces"]
JOB_ARGS_FORMAT = "-step {step} -fr {start} {end} {args} -root {root} -file {path}"