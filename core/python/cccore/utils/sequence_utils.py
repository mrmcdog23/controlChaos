""" Utilities for image and cache sequences """
import re
import sys
import os
import shutil
import glob
from typing import Optional, Any
import cccore.utils.sequence_data as sequence_data
import cccore.utils.file_utils as file_utils
import cccore.utils.cc_logging as cc_logging
import cccore.data.server_data as server_data
#import cccore.utils.apply_hud as apply_hud
import cccore.file_env.context_utils as context_utils
import cccore.core_constants as core_constants


logger = cc_logging.cc_logger()


def list_sequences(image_dir):
    # type: (str) -> None
    """
    List the sequences in a linux shell

    Args:
        image_dir: Path of the images directory to check
    """
    files_found = file_utils.get_files_recursively(image_dir)
    if not files_found:
        print("No files in folder")
        return

    sequences_data = sequences_data_from_dir(image_dir)
    print("\n")
    for seq_data in sequences_data:
        if not seq_data.missing_frames:
            print(f"{seq_data.padded_path} {seq_data.frame_range}")
        else:
            print(seq_data.padded_path,
                  seq_data.frame_range,
                  f"\tMissing: {seq_data.missing_frames_text}"
                  )


def is_sequence_path(image_path):
    # type: (str) -> bool
    """
    Is an image path a sequence

    Args:
        image_path: Path of the sequence

    Returns:
        True if sequence
    """
    frame_num = image_path.split(".")[1]
    return frame_num.isdigit()


def get_sequence_data(frame_file_path):
    # type: (str) -> sequence_data.SequenceData
    """
    Get the data of one sequence from the file path or hashed

    Args:
        frame_file_path: Frame path e.g: /job/path/render.3243.exr
                                               /job/path/render.####.exr

    Returns:
        Data of the sequence
    """
    return sequence_data.SequenceInfo(frame_file_path).seq_data


def make_sequence_read_only(sequence_path):
    # type: (str) -> None
    """
    Make all the images in a sequence read only

    Args:
        sequence_path: Path of the image sequence
    """
    seq_data = get_sequence_data(sequence_path)
    for frame_path in seq_data.frame_paths:
        os.chmod(frame_path, 0o440)


def get_image_file_name(output_image):
    # type: (str) -> str
    """
    Get the image name taking into account
    there might not be 2 decimals

    Args:
        output_image: The image base name

    Returns:
        file_name: The file name without the frame number
    """
    file_name = file_utils.get_file_name(output_image)
    if output_image.count(".") == 1:
        frame_num_found = re.findall(r'\d+', output_image)
        if frame_num_found:
            frame_number = frame_num_found[-1]
            root_file_name = file_name.split(frame_number)[0]
            return root_file_name
    return file_name


def sequences_data_from_dir(directory_path):
    # type: (str) -> list[sequence_data.SequenceData]
    """
    Find all sequences in a directory

    Args:
        directory_path: The source directory

    Returns:
        sequences_data: List of sequence datas
    """
    # remove end slash for the glob
    if directory_path.endswith("/"):
        directory_path = directory_path[:-1]

    # get a set of all images sequence names in the folder
    output_images = os.listdir(directory_path)
    image_names_set = set()
    image_types = tuple(core_constants.SEQUENCE_TYPES)
    for output_image in output_images:
        if not output_image.endswith(image_types):
            continue
        image_file_name = get_image_file_name(output_image)
        image_names_set.add(image_file_name)

    # from the image names get the sequence data classes
    sequences_data = list()
    for image_name in image_names_set:
        image_path = glob.glob(directory_path + f"/{image_name}*")[0]
        seq_data = get_sequence_data(image_path)
        sequences_data.append(seq_data)
    return sequences_data


def get_sequences_recursively(directory_path):
    # type: (str) -> list[sequence_data.SequenceData]
    """
    List all the sequences from a directory recursively

    Args:
        directory_path: The source directory

    Returns:
        sequences_data: List of sequence datas
    """
    all_files = file_utils.get_files_recursively(directory_path)
    folder_paths = set()
    for file_path in all_files:
        folder_paths.add(os.path.dirname(file_path))

    sequences_data = list()
    for folder_path in folder_paths:
        sequences_data.extend(sequences_data_from_dir(folder_path))
    return sequences_data


def get_most_recent_padded_path(directory_path):
    # type: (str) -> str
    """
    Most recent sequence in a directory

    Args:
        directory_path: The source directory

    Returns:
        padded_path: The most recent path padded
    """
    sequences_data = sequences_data_from_dir(directory_path)
    if sequences_data == 1:
        return sequences_data[0].padded_path

    # combine all the file paths
    frame_paths = list()
    for seq_data in sequences_data:
        frame_paths.extend(seq_data.frame_paths)

    latest_file = max(frame_paths, key=os.path.getctime)
    seq_data = get_sequence_data(latest_file)
    return seq_data.padded_path


def convert_frame_to_sequence(frame_path):
    # type: (str) -> str
    """
    Convert a frame path to a sequence

    Args:
        frame_path: Frame path e.g: /job/path/render.3243.exr

    Returns:
        sequence_path: Sequence path e.g: /job/path/render.####.exr
    """
    sequence_name, _, ext = frame_path.split(".")
    sequence_path = f"{sequence_name}.####.{ext}"
    return sequence_path


def convert_sequence_to_frame(sequence_path):
    # type: (str) -> str
    """
    Convert a sequence to the first frame on disk path

    Args:
        sequence_path: Sequence path e.g: /job/path/render.####.exr

    Returns:
        frame_path: Frame path e.g: /job/path/render.3231.exr
    """
    sequence_name, _, ext = sequence_path.split(".")
    frame_paths = glob.glob(f"{sequence_name}.*.{ext}")
    frame_paths.sort()
    if not frame_paths:
        return
    return frame_paths[0]


def slack_sequence_text(shots_list, start=None, end=None):
    # type: (list[str], Optional[int], Optional[int]) -> str
    """
    Create sequence string to display on Slack from a list of shots

    Args:
        shots_list: List of shots to create text for
        start: First frame of the sequence
        end: Last frame of the sequence

    Returns:
        sequence_text: Text slack display text
    """
    first_shot = shots_list[0]
    ctx = context_utils.get_context_from_path(first_shot)

    # split sequence at root and get the version directory
    split_text = f"/{ctx.version_padded}/"
    root_dir = first_shot.split(split_text)[0]
    version_dir = f"{root_dir}/{ctx.version_padded}"

    # split the sequences at the root
    sequence_text = f"{version_dir}\n"
    for sequence_path in shots_list:
        render_path = sequence_path.split(f"{version_dir}/")[1]

        # if the start and end frame wasn't provided get it from the sequence
        if not start or not end:
            seq_data = get_sequence_data(sequence_path)
            start = seq_data.start
            end = seq_data.end

        # build the display text with the frame range first
        sequence_text += f"{start}-{end}   {render_path}\n"
    return sequence_text


def copy_sequence(wip_sequence, pub_sequence, log=None):
    # type: (str, str, Optional[Any]) -> None
    """
    Copy a sequence from one location to another

    Args:
        wip_sequence: The source sequence path
        pub_sequence: The destination sequence path
        log: The log function
    """
    seq_data = get_sequence_data(wip_sequence)
    file_utils.create_directories(os.path.dirname(pub_sequence))
    log = log or logger.info
    log(f"Source Sequence: {wip_sequence}")
    log(f"Destination Sequence: {pub_sequence}")

    # exception for alembics
    if seq_data.is_single_frame:
        log(f"Single Frame Sequence")
        shutil.copy(wip_sequence, pub_sequence)
        return pub_sequence

    source_format_path = seq_data.format_path
    frame_count = seq_data.frame_count

    hashed = seq_data.padding * "#"
    pub_sequence_format = pub_sequence.replace(hashed, "{frame}")
    for index, frame in enumerate(seq_data.frames_str):
        source_path = source_format_path.format(frame=frame)
        dest_path = pub_sequence_format.format(frame=frame)

        log(f"---- {index} of {frame_count} ----")
        log(source_path)
        log(dest_path)
        try:
            shutil.copy(source_path, dest_path)
        except PermissionError:
            continue

    return pub_sequence


def convert_sequence_to_tx_file(pub_sequence):
    # type: (str) -> list[str]
    """
    Convert a sequence to tx files using make tx

    Args:
        pub_sequence: Sequence to convert to tx files

    Returns:
        tx_file_path_list: Generated tx file paths
    """
    project_data = server_data.ProjectData()
    maketx = project_data.maketx
    seq_data = get_sequence_data(pub_sequence)
    logger.info("----")
    logger.info("Converting frames to tx files")

    tx_file_path_list = list()
    for frame_path in seq_data.frame_paths:
        path_no_ext, _ = os.path.splitext(frame_path)
        tx_frame_path = f"{path_no_ext}.tx"
        maketx_cmd = f"{maketx} {frame_path} -o {tx_frame_path}"
        logger.info("----")
        logger.info(frame_path)
        logger.info(tx_frame_path)
        os.system(maketx_cmd)
        tx_file_path_list.append(tx_frame_path)
    return tx_file_path_list


def get_frame_number(full_image_name):
    # type: (str) -> Optional[int]
    """
    Get the frame number from an image name

    Args:
        full_image_name: Image path to get the number for

    Returns:
        The frame number
    """
    frame_nums = re.findall(r'\d+', full_image_name)
    if not frame_nums:
        return None
    return int(frame_nums[-1])


def get_path_from_number(source_path, frame_num):
    # type: (str, str) -> str
    """
    From a sequence file path and a number
    work out the file path

    Args:
        source_path: Source file path
        frame_num: The frame number to get

    Returns:
        file_path: Path of the frame number file
    """
    path, _, ext = source_path.split(".")
    frame_num_padded = str(frame_num).zfill(4)
    file_path = f"{path}.{frame_num_padded}.{ext}"
    return file_path


def convert_to_hash(write_path):
    # type: (str) -> str
    """
    Convert the write path to hashes
    sequence.%04d.exr -> sequence.####.exr

    Args:
        write_path: Write path in nuke format

    Returns:
        hash_path: Path of the write hashes
    """
    if write_path.count(".") != 2:
        return write_path
    path, _, extension = write_path.split(".")
    hash_path = f"{path}.####.{extension}"
    return hash_path


def apply_hud_to_mov(source_movie_path, artist_name):
    # type: (str, str) -> str
    """
    Apply the cc hud on to the mov file
    and generate a new movie file

    Args:
        source_movie_path: Path of the source movie file
        artist_name: Name of the artist that submitted it

    Returns:
        hud_mov_path: Path to the new movie file
    """
    artist_name = artist_name or os.environ["USER"]
    out_temp = os.path.join(server_data.ProjectData().appdata, "output")
    file_utils.create_directories(out_temp)
    image_name = file_utils.get_file_name(source_movie_path)
    image_name = image_name.replace(" ", "_")
    image_sequence = f"{out_temp}/{image_name}.%04d.png"
    ffmpeg_command = f'ffmpeg -i "{source_movie_path}" "{image_sequence}"'
    logger.info(f"Running: {ffmpeg_command}")
    os.system(ffmpeg_command)

    # gather the sequence data
    logger.info(f"Finding sequence data: {image_sequence}")
    seq_data = get_sequence_data(image_sequence)
    image_name = seq_data.image_name
    file_utils.create_directory(out_temp)
    path_suffix = f"{out_temp}/{image_name}."
    hud_mov_path = f"{path_suffix}mov"
    logger.info(f"Output path: {hud_mov_path}")

    data = {
        "mov_path": hud_mov_path,
        "path_suffix": path_suffix,
        "start": seq_data.start,
        "end": seq_data.end,
        "playable_component": image_sequence,
        "shot_name": image_name,
        "artist_name": artist_name
    }
    apply_hud.create_cc_hud_mov(data)

    # remove generated file paths
    for frame_path in seq_data.frame_paths:
        if "appdata" in frame_path:
            os.remove(frame_path)

    return hud_mov_path


def get_image_name(source_image_path):
    # type: (str) -> str
    """
    Get the image name if it's in the cc conventions

    Args:
        source_image_path: The path of the file image file

    Returns:
        image_name: The name of the image without the padding
    """
    image_basename = os.path.basename(source_image_path)
    found = re.search(core_constants.cc_IMAGE_CONVENTION, image_basename)
    if found:
        image_name = found.groups()[0]
    else:
        image_name = image_basename.split(".")[0]
    return image_name


if __name__ == "__main__":
    image_directory = sys.argv[1]
    list_sequences(image_directory)
