import os


def get_relative_path(path_suffix):
    pipeline_root_dir = os.environ["PIPELINE_ROOT"]
    relative_path = os.path.join(pipeline_root_dir, path_suffix)
    relative_path_clean = relative_path.replace("\\", "/")
    return relative_path_clean