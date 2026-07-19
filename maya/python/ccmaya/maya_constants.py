TRANSLATE = ["tx", "ty", "tz"]
ROTATE    = ["rx", "ry", "rz"]
SCALE     = ["sx", "sy", "sz"]
VISIBILITY = ["v"]


DEFAULT_CAMERAS = ["persp", "top", "front", "side"]
EXPORT_GROUPS = ["GEO", "CAM"]
GEO_GROUP = "GEO"
CAM_GROUP = "CAM"
JNT_GROUP = "JNT"

# alembic arguments
MESH_ABC_ARGS = ["-uvWrite", "-writeVisibility", "-writeUVSets",
                 "-worldSpace", "-dataFormat", "ogawa", "-stripNamespaces"
                 ]
CAM_ABC_ARGS = ["-worldSpace", "-stripNamespaces"]
JOB_ARGS_FORMAT = "-step {step} -fr {start} {end} {args} -root {root} -file {path}"