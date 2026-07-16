import os
import yaml
import json


def read_yaml(file_path):
    """
    Read a yaml file and store the data

    Args:
        file_path: Path of the yaml to read

    Returns:
        data: The data of the yaml
    """
    with open(file_path) as file:
        data = yaml.safe_load(file)
    return data


def write_json(file_path, data):
    """
    Write a json file and store the data

    Args:
        file_path: Path of the json to write
        data: The data of the json
    """

    # write the metadata to the file
    with open(file_path, 'w') as open_file:
        json.dump(data, open_file, indent=4, sort_keys=True)


def read_json(json_path):
    # type: (str) -> Optional[dict]
    """
    From a json file read and return the data

    Args:
        json_path: Path of the json file to read

    Returns:
        data: Information from the json
    """
    if not os.path.exists(json_path):
        return None

    with open(json_path, 'r') as f:
        data = json.load(f)
    return data