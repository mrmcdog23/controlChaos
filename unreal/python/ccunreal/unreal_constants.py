""" Unreal constants """
import unreal as ue


MATERIAL = "Material"
SKELETON = "Skeleton"
SKELETON_MESH = "SkeletalMesh"
STATIC_MESH = "StaticMesh"
ANIM_SEQUENCE = "AnimSequence"
IGNORE_IMPORT_TYPES = [
    "FbxSceneImportData",
    "Blueprint",
    SKELETON,
    SKELETON_MESH,
    STATIC_MESH
]

LS_PREFIX = "LS"
MP_PREFIX = "MP"

SUPPORTED_EXPORT_CLASSES = [
    ue.SkeletalMeshActor,
    ue.StaticMeshActor,
    ue.CineCameraActor
]
