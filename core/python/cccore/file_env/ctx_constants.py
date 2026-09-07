# create constants
ASSET = "asset"
SEQUENCE = "sequence"
ENTITY = "entity"

# asset names
ASSET_BUILD_TYPE_NAME = "asset_type"
ASSET_BUILD_NAME = "asset_name"
TASK_NAME = "task_name"

# shot names
SEQUENCE_NAME = "sequence_name"
SHOT_NAME = "shot_name"
VER = "version_num"

# define lists and dictionary
ENTITIES = [ASSET, SEQUENCE]
ASSET_ORDER = [ENTITY, ASSET_BUILD_TYPE_NAME, ASSET_BUILD_NAME, TASK_NAME]
SHOT_ORDER = [ENTITY, SEQUENCE_NAME, SHOT_NAME, TASK_NAME]
ENTITY_DICT = {ASSET: ASSET_ORDER, SEQUENCE: SHOT_ORDER}

APP_FILE_SUBFOLDER = {
    "maya": "scenes",
    "nuke": "scripts"
}

SHOT_KEYS = [
    "entity",
    "sequence_name",
    "shot_name",
    "app_name",
    "subfolder",
    "task_name",
    "username",
    "file_name"
]

ASSET_KEYS = [
    "entity",
    "asset_type",
    "asset_name",
    "app_name",
    "subfolder",
    "task_name",
    "username",
    "file_name"
]

CONTEXT_PANEL = 'context_panel'
CONTEXT_BTNS = "import ccmaya.startup.context_buttons as context_buttons;" \
               "ctx = context_buttons.ContextButtons()"