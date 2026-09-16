""" Post process template to log the progress of the cache """
import re
import os
import glob
from typing import Optional
import cccore.utils.cc_logging as cc_logging
import cccore.utils.sequence_utils as sequence_utils


EXTRACT_REGEX = r"(.*)/(\w+).([0-9]+).(.*)"
CACHE_OUTPUT_PATH = "CACHE_PATH"
START = START_FRAME
END = END_FRAME
LOGGER = cc_logging.cc_logger()


def get_source_file_path():
    # type: () -> Optional[str]
    """
    Find the source frame to get the sequence data for

    Returns:
        The source image path found
    """
    if os.path.exists(CACHE_OUTPUT_PATH):
        return CACHE_OUTPUT_PATH

    found = re.search(EXTRACT_REGEX, CACHE_OUTPUT_PATH)
    if not found:
        return str()
    path, filename, number, extension = found.groups()
    try:
        source_file_path = glob.glob(f"{path}/{filename}.*.{extension}")[0]
        return source_file_path
    except IndexError:
        LOGGER.critical("No files found on disk")


def main():
    """
    Get the last frame rendered and work out the percentage completed
    """
    source_file_path = get_source_file_path()
    if not source_file_path:
        return
    seq_data = sequence_utils.get_sequence_data(source_file_path)

    # get the last frame and work out the number of frames
    last_frame_number = seq_data.frames[-1]
    number_of_frames = float(last_frame_number - START)

    # get the total as a percentage
    total = float(END - START)
    progress_decimal = number_of_frames / total
    progress_percent = int(progress_decimal * 100)

    # if its over 100 set to 99 to not complete the job
    if progress_percent >= 100:
        progress_percent = 99

    # log the percentage to get deadline to add the progress
    LOGGER.info(f"Progress: {progress_percent}%.")


main()
