import os
import sys


def reload_cc_modules():
    """
    Reload all control chaos modules
    """
    to_remove = list()
    for k, v in sys.modules.items():
        if k.startswith("cc"):
            to_remove.append(k)
    for e in to_remove:
        print(f"Reloading...{e}")
        del sys.modules[e]


def join_file_names(*folder_list):
    # type: (Any) -> str
    """
    Join folder names and create a path from

    Args:
        folder_list: Names of files to join

    Returns:
        folder_path_clean: the joined path of names clean
    """
    if isinstance(folder_list[0], list):
        folder_path = "/".join(folder_list[0])
    else:
        folder_path = os.path.join(*folder_list)
    folder_path_clean = folder_path.replace("\\", "/")
    return folder_path_clean