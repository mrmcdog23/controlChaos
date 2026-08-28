""" Get data on sequences such as caches and images """
import re
import os
import glob
from typing import Optional
from dataclasses import dataclass, field
import cccore.core_constants as core_constants
import cccore.utils.cc_logging as cc_logging


@dataclass
class SequenceData:
    """
    Data class for gathering sequence data
    """
    frames: list[int] = field(default_factory=list)
    missing_frames: list[int] = field(default_factory=list)
    missing_frames_text: str = str()
    frames_str: list[str] = field(default_factory=list)
    frame_paths: list[str] = field(default_factory=list)
    disk_versions: list[str] = field(default_factory=list)
    image_name: str = str()
    image_path: str = str()
    frame_range: str = str()
    extension: str = str()
    hashes: str = str()
    padding: int = int()
    padded_name: str = str()
    path_basename: str = str()
    images_dir: str = str()
    padded_path: str = str()
    houdini_path: str = str()
    houdini_path_unpadded: str = str()
    first_frame_path: str = str()
    nuke_path: str = str()
    format_path: str = str()
    regex_path: str = str()
    first_frame: str = str()
    current_frame: int = int()
    prefix: str = str()
    version: str = str()
    start: int = int()
    frame_count: int = int()
    end: int = int()
    is_cache: bool = bool()
    is_image: bool = bool()
    is_single_frame: bool = bool()


@dataclass
class SequenceInfo(object):
    """
    Get all sequence data from an image path
    """
    def __init__(self, source_image_path):
        # type: (str) -> None
        """
        Args:
            source_image_path: Path of the image to check
        """
        # initialize class variables
        self.images_dir = str()
        self.logger = cc_logging.cc_logger()
        self.source_image_path = self.get_source_image_path(source_image_path)

        # initialize sequence data
        self.seq_data = SequenceData()

        self.get_matching_sequence_files()

        if self.seq_data.is_single_frame:
            self.get_single_frame_data()
        else:
            self.get_sequence_data()

    @staticmethod
    def get_source_image_path(source_image_path):
        # type: (str) -> str
        """
        Get the source path on disk. This is for padded paths

        Args:
            source_image_path: The source image path

        Returns:
            The source image path found
        """
        # if the path exists return it
        # if the path exists return it
        if os.path.exists(source_image_path):
            return source_image_path

        # if there are no hashes in path return it
        frame_expression = re.findall(r'\$F4|%04d|#####|####|\.\d+\.', source_image_path)
        if frame_expression:
            matching_expressions = [e for e in frame_expression if e]
            use_expression = matching_expressions[-1].strip(".")
        else:
            raise FileNotFoundError(f"No files on disk: {source_image_path}")

        # get the regex of the source path
        regex_source_image = source_image_path.replace(use_expression, "*")
        files_found_on_disk = glob.glob(regex_source_image)
        if not files_found_on_disk:
            raise FileNotFoundError(f"No files on disk of padding: {source_image_path}")

        # return the first file found
        return files_found_on_disk[0]

    def get_matching_sequence_files(self):
        """
        Get all matching file names by replacing the frame
        number with a star and searching for matches
        """
        self.images_dir = os.path.dirname(self.source_image_path)
        file_name = os.path.basename(self.source_image_path)

        if not os.path.exists(self.images_dir):
            self.logger.debug(f"File does not exist: {self.images_dir}")
            return list()

        # extract the information to get all sequences
        matching_file_name = re.search(r'(.*)([.|_|v])(\d+).(.*)', file_name)
        if not matching_file_name or not matching_file_name.groups():
            self.logger.warning(f"No data found in file name: {file_name}")
            self.seq_data.is_single_frame = True
            return

        # fix for underscore sequences rather than decimals
        if file_name.count(".") == 1:
            prefix = "_"
            frame = 1001

            # for files with underscores rather than decimals
            matching_file_name = re.search(r'(.*)_(\d+).(.*)', file_name)
            if matching_file_name:
                image_name, frame, extension = matching_file_name.groups()
                file_name_regex = file_name.replace(frame, "*")
                full_regex = f"{self.images_dir}/{file_name_regex}"
                frame_paths = glob.glob(full_regex)
                frame_paths.sort()
            else:
                image_name, extension = os.path.splitext(file_name)
                full_path = f"{self.images_dir}/{file_name}"
                frame_paths = [full_path]
        else:
            # get all matching sequences
            image_name, prefix, frame, extension = matching_file_name.groups()
            if "." in extension and extension != "bgeo.sc":
                prefix = str()
                try:
                    image_name, frame, extension = file_name.split(".")
                except ValueError:
                    self.logger.warning(f"Invalid path: {self.images_dir}/{file_name}")
                    return
            regex = f"{self.images_dir}/{image_name}{prefix}*.{extension}"
            frame_paths = glob.glob(regex)
            frame_paths.sort()

        # if no frames were found then quit
        if not frame_paths:
            raise FileNotFoundError(f"No files found: {self.source_image_path}")

        # set the data on the class
        self.seq_data.frame_paths = frame_paths
        self.seq_data.images_dir = self.images_dir
        self.seq_data.extension = extension
        self.seq_data.is_single_frame = len(frame_paths) == 1
        self.seq_data.first_frame_path = frame_paths[0]
        self.seq_data.current_frame = int(frame)
        self.seq_data.frames.append(int(frame))
        self.seq_data.frames_str.append(frame)
        self.seq_data.image_name = image_name
        self.seq_data.prefix = prefix
        self.seq_data.is_cache = extension in core_constants.CACHE_TYPES
        self.seq_data.is_image = extension in core_constants.IMAGE_TYPES
        self.seq_data.image_path = self.source_image_path

    def get_single_frame_data(self):
        """
        Get the alembic path data
        """
        current_frame = self.seq_data.current_frame
        self.seq_data.padded_name = os.path.basename(self.source_image_path)
        self.seq_data.padded_path = self.source_image_path
        self.seq_data.houdini_path = self.source_image_path
        self.seq_data.first_frame_path = self.source_image_path
        self.seq_data.nuke_path = self.source_image_path
        self.seq_data.frame_paths = [self.source_image_path]
        self.seq_data.start = current_frame
        self.seq_data.end = current_frame
        self.seq_data.frame_range = f"{current_frame}-{current_frame}"
        self.seq_data.frame_count = len(self.seq_data.frame_paths)
        self.seq_data.disk_versions = self.disk_versions

    @property
    def disk_versions(self):
        # type: () -> list[str]
        """
        Get a versions on disk. Use the image directory

        Returns:
            version_nums: List of version folders on disk
        """
        versions_dir = os.path.dirname(self.source_image_path)
        task_dir = os.path.dirname(versions_dir)
        version_folders = os.listdir(task_dir)
        version_nums = [ver for ver in version_folders if ver.isdigit()]
        version_nums.sort()
        version_nums.reverse()
        return version_nums

    @staticmethod
    def frame_number(full_image_name):
        # type: (str) -> Optional[str]
        """
        Get the frame number from an image name

        Args:
            full_image_name:

        Returns:
            The image number
        """
        frame_nums = re.findall(r'\d+', full_image_name)
        if not frame_nums:
            return None
        return frame_nums[-1]

    @staticmethod
    def find_missing_frames(frames_found):
        # type: (list[int]) -> list[int]
        """
        Search for missing frames in a list

        Args:
            frames_found: Image numbers

        Returns:
            List of missing images
        """
        return [i for x, y in zip(frames_found, frames_found[1:])
                for i in range(x + 1, y) if y - x > 1]

    @staticmethod
    def convert_frame_list_to_text(missing_frames):
        # type: (list[int]) -> str
        """
        Convert a list of missing frames to text format to make it more readable

        Args:
            missing_frames: List of missing frames

        Returns:
            frames_text_str: Text format of missing frames
        """
        frames_text_list = list()
        next_missing_frames = list()
        for index, current_frame_num in enumerate(missing_frames):

            # get the next frame number in the list
            try:
                next_in_list = missing_frames[index + 1]
            except IndexError:
                pass
            next_frame_num = current_frame_num + 1

            # if the next frame number is the next one then
            # add to the next missing frame list
            if next_frame_num == next_in_list:
                 next_missing_frames.append(current_frame_num)
            else:
                if next_missing_frames:
                    # if there is a missing frame list then convert it to text
                    text = f"{next_missing_frames[0]}-{current_frame_num}"
                    next_missing_frames = list()
                    frames_text_list.append(text)
                else:
                    frames_text_list.append(str(current_frame_num))

        # convert the list of text to one string
        frames_text_str = ", ".join(frames_text_list)
        return frames_text_str

    def get_all_frame_numbers(self):
        """
        Get the frame numbers in int and string from and
        """
        for image_path in self.seq_data.frame_paths:
            frame_num = self.frame_number(image_path)
            self.seq_data.frames.append(int(frame_num))
            self.seq_data.frames_str.append(frame_num)
        self.seq_data.frames_str.sort()
        if self.seq_data.frames_str:
            self.seq_data.first_frame = self.seq_data.frames_str[0]

    def get_sequence_data(self):
        """
        Get images data from a directory
        """
        # get the frame numbers in int and string from and
        self.get_all_frame_numbers()
        if not self.seq_data.frames:
            return

        # get a list of the missing frames
        self.seq_data.missing_frames = self.find_missing_frames(self.seq_data.frames)
        self.seq_data.missing_frames_text = self.convert_frame_list_to_text(self.seq_data.missing_frames)

        # use the first frame for the padding
        start = min(self.seq_data.frames)
        end = max(self.seq_data.frames)
        self.seq_data.start = start
        self.seq_data.end = end
        self.seq_data.frame_range = f"{start}-{end}"
        self.seq_data.frame_count = len(self.seq_data.frames)

        # work out the padded path
        padding = len(self.seq_data.frames_str[0])
        self.seq_data.padding = padding
        hashed = "#" * self.seq_data.padding
        houdini_exp = f"$F{self.seq_data.padding}"
        nuke_exp = f"%0{self.seq_data.padding}d"

        extension = self.seq_data.extension
        image_name = self.seq_data.image_name
        prefix = self.seq_data.prefix
        padded_name = f"{image_name}{prefix}{hashed}.{extension}"
        padded_path = os.path.join(self.images_dir, padded_name)

        self.seq_data.padded_name = padded_name
        self.seq_data.padded_path = padded_path
        self.seq_data.format_path = padded_path.replace(hashed, "{frame}")
        self.seq_data.regex_path = padded_path.replace(hashed, "*")
        self.seq_data.houdini_path = padded_path.replace(hashed, houdini_exp)
        self.seq_data.houdini_path_unpadded = padded_path.replace(hashed, "$F")
        self.seq_data.nuke_path = padded_path.replace(hashed, nuke_exp)
        self.seq_data.path_basename = padded_path.split(hashed)[0]
        self.seq_data.disk_versions = self.disk_versions

