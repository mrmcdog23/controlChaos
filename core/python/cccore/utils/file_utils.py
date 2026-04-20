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


def get_files_recursively(directory, extensions=None):
    # type: (str, list[str]) -> Optional[list[str]]
    """
    Get all sub files of type recursively

    Args:
        directory: Path of the directory to check
        extensions: File types to file

    Returns:
        list_of_files: List of files found
    """
    list_of_files = list()
    extensions_set = tuple(extensions) if extensions else None
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            if not extensions_set:
                file_path = join_file_names([root, file_name])
                list_of_files.append(file_path)

            elif file_name.endswith(extensions_set):
                file_path = join_file_names([root, file_name])
                list_of_files.append(file_path)
    return list_of_files


def get_file_name(file_path):
    # type: (str) -> str
    """
    Get the file name from the file path.
    e.g. /home/docs/filename.ext will return filename

    Args:
        file_path: The original file path

    Returns:
        file_name: Name of the file with no extension
    """
    basename = os.path.basename(file_path)
    file_name, _ = os.path.splitext(basename)
    if "." in file_name:
        file_name = file_name.split(".")[0]
    return file_name