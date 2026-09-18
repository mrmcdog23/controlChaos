""" General houdini constants """
TAB_NAMES_LIST = ["PerformanceMonitor"]

RENDER_NODE_TYPES = ["arnold", "ifd", "karma"]

RENDER_NODES_DICT = {"arnold": "arnold",
                     "mantra": "ifd",
                     "ifd": "mantra",
                     "karma": "karma",
                     "comp": "comp"
                     }

SUBMITTER = "ccsubmit"

ROP_TYPE_TO_PICTURE_PARM = {
    "arnold": "ar_picture",
    "ifd": "vm_picture",
    "karma": "picture",
    "comp": "copoutput"
}

# commercial templates
LIGHTING_TEMPLATE_200590 = "lightingTemplateNewFolders_200590.hip"
LIGHTING_TEMPLATE_205445 = "lightingTemplateNewFolders_205445.hip"
LOOKDEV_TEMPLATE = "lookdevTemplate_205445.hip"
GROOM_TEMPLATE = "groomTemplate_v1.hip"


# longform templates
LIGHTING_TEMPLATE_LF_205445 = "lightingTemplateLongform_205445.hip"
LOOKDEV_TEMPLATE_LF_205445 = "lookdevTemplateLongform_205445.hip"

FILE_TEMPLATES = [
    LIGHTING_TEMPLATE_205445,
    LOOKDEV_TEMPLATE,
    GROOM_TEMPLATE,
    LIGHTING_TEMPLATE_LF_205445,
    LOOKDEV_TEMPLATE_LF_205445
]

CC_FRAME_RANGE = "cc_frame_range"

USE_CACHE_PARM_NAME = "use_cache_path"
