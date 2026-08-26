import os
import re
import cccore.file_env.ctx_constants as ctx_constants
import cccore.file_env.context as context
import cccore.utils.cc_logging as cc_logging


def get_display_text(envvar, selected_text):
    # type: (str, str) -> str
    """
    Get the text to be displayed on the context button

    Args:
        envvar: Environment variable name
        selected_text: Selected text of the environment var

    Returns:
        display_text: Text to set on the button
    """
    if envvar == ctx_constants.SEQUENCE_NAME:
        display_text = selected_text
    elif envvar == ctx_constants.SHOT_NAME:
        display_text = selected_text.replace("sh", "")
    elif envvar == ctx_constants.TASK_NAME:
        display_text = selected_text[:4]
    else:
        display_text = selected_text[:]
    return display_text[:5]


def get_btn_label(envvar):
    # type: (str) -> str
    """
    The default text to set on the button

    Args:
        envvar: Environment variable name

    Returns:
        label: Label text to set on the button
    """
    if envvar == ctx_constants.ASSET_BUILD_NAME:
        return "name"
    text = envvar.replace("_name", "")
    label = text.split("_")[-1] if "asset_" in text else text[:5]
    return label


def context_dict_from_path(path):
    # type: (str) -> dict
    """
    From a file path build a context dictionary

    Args:
        path: The file path to get the data from

    Returns:
        context_dict: The context dictionary
    """
    context_dict = dict()
    project_root = os.environ["PROJECT_ROOT"]

    # make sure the path starts with the project root
    if not path.startswith(project_root):
        logger = cc_logging.cc_logger()
        logger.warning(f"Project root {project_root} not found in path")
        return context_dict

    # extract the values from the path
    no_root_path = path.replace(project_root + "/", str())
    values = no_root_path.split("/")

    # build the dictionary of the context values
    for index, value in enumerate(values):
        key = ctx_constants.SHOT_KEYS[index]
        context_dict[key] = value

    # extract the values from the file name
    file_name = context_dict.get("file_name")
    if not file_name:
        return context_dict

    # extract the extension
    extension = file_name.split(".")[-1]
    context_dict["ext"] = extension

    # get the version number
    version_match = re.match(r"(.*)_v(\d+).(.*)", file_name)
    if version_match:
        context_dict["version_padded"] = version_match.group(2)

    # extract the suffix if there is one
    has_suffix = file_name.count("_") == 5
    if not has_suffix:
        return context_dict

    # build the regex to extract the suffix
    regex = r"(.*)" + context_dict["task_name"] + "_(.*)_v(.*)"
    suffix_match = re.match(regex, file_name)
    if suffix_match:
        context_dict["suffix"] = suffix_match.group(2)
    return context_dict


def get_context_from_path(path):
    # type: (str) -> context.Context
    """
    From a file path build a context class instance

    Args:
        path: The file path to get the data from

    Returns:
        ctx: The context dictionary
    """
    context_dict = context_dict_from_path(path)
    ctx = context.Context(overrides=context_dict)
    return ctx