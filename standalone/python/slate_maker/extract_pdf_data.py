import re
import os
import pdfplumber
import subprocess
import datetime
import tempfile
import logging
from dataclasses import dataclass
import cccore.core_constants as core_constants


# constants
logging.basicConfig(level=logging.INFO)


FFMPEG_EXE = core_constants.FFMPEG_EXE
THUMBNAIL_SIZE = "750x450"
FONT_SIZE = "35"
current_dir = os.path.dirname(__file__).replace("\\", "/")
DRIVE_LETTER = current_dir[0]
NO_DRIVE_PATH = current_dir[3:]
NO_THUMBNAIL = f"{current_dir}/nothumbnail.png"
BLANK_SLATE = f"{current_dir}/blank_slate.png"
TEXT_FORMAT = ("drawtext=fontfile={DRIVE_LETTER}\\\:/{NO_DRIVE_PATH}/Roboto-Regular.ttf:text='{text}'"
               ":fontcolor=white:fontsize={font_size}:x=245:y={ypos}")


@dataclass
class PDFData:
    """ Data class for gathering PDF data """
    show_name: str = str()
    shot_name: str = str()
    duration: str = str()
    focal_length: str = str()
    thumbnail_path: str = NO_THUMBNAIL
    resolution: str = str()
    version: str = str()
    notes: str = str()


class ExtractData(object):
    """
    Extract the data from the PDF and generate slates and thumbnails
    """
    def __init__(self, movie_dir):
        # type: (str) -> None
        """
        Args:
            movie_dir: Movie directory path
        """
        self.movie_dir = movie_dir
        self.logger = logging.getLogger(__name__)
        self.pages_text = list()
        self.shot_name = str()
        self.pdf_path = str()
        self.pdf_data = PDFData()

    def get_shot_name(self, pdf_path):
        # type: (str) -> str
        """
        Get the name of the shot from the pdf file

        Args:
            pdf_path: Path of the pdf file

        Returns:
            shot_name: Name of the shot to use
        """
        pdf_base_name = os.path.basename(pdf_path)
        shot_name = pdf_base_name.split("_rev")[0]
        return shot_name

    def get_data_from_pdf(self, pdf_path):
        # type: (str) -> PDFData
        """
        From a PDF path get the data and generate a thumbnail

        Args:
            pdf_path: Path of the PDF to extract data

        Returns:
            pdf_data: The PDF data class
        """
        self.pdf_data = PDFData()
        self.extract_with_pdfplumber(pdf_path)
        shot_name = self.get_shot_name(pdf_path)
        self.build_data_dict(shot_name)
        self.generate_thumbnail()
        return self.pdf_data

    def run_ffmpeg_command(self, command):
        # type: (str) -> None
        """
        Run the ffmpeg subprocess

        Args:
            command: The command to run
        """
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        process.communicate()

    def extract_with_pdfplumber(self, pdf_path):
        # type: (str) -> None
        """
        Extract all information from the given PDF file path

        Args:
            pdf_path: Path of the PDF to extract data for
        """
        self.pages_text = list()
        self.logger.info(f"Reading: {pdf_path}")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    self.pages_text.extend(text.split("\n"))

        except pdfplumber.utils.exceptions.PdfminerException:
            pass

    def build_data_dict(self, shot_name):
        """
        From the list of page text get the data of the shot
        """
        self.pdf_data.resolution = "n/a"
        self.pdf_data.version = "n/a"
        self.pdf_data.notes = "n/a"
        self.pdf_data.shot_name = shot_name
        self.pdf_data.show_name = self.pages_text[0].title()

        for index, line in enumerate(self.pages_text):
            if "Work In" in line:
                range_line = self.pages_text[index + 1]
                numbers = range_line.split(" ")
                start_frame = numbers[0]
                end_frame = numbers[-1]
                self.pdf_data.duration = f"{start_frame}-{end_frame}"

            if self.pdf_data.focal_length:
                continue
            # extract the focal length and set in the data
            focal_length_match = re.search(r"(.*) (\d+)([mm|MM])", line)
            if focal_length_match:
                self.pdf_data.focal_length = focal_length_match.groups()[1] + "mm"
                continue

            focal_length_match = re.search(r"(\d+)MM", line)
            if focal_length_match:
                self.pdf_data.focal_length = focal_length_match.groups()[0] + "mm"

    def generate_thumbnail(self):
        """
        Generate the thumbnail from the source movie file
        """
        # find the movie file path
        movie_file_path = None
        for movie_file in os.listdir(self.movie_dir):
            if movie_file.startswith(self.pdf_data.shot_name) and movie_file.endswith((".mp4", ".mov")):
                movie_file_path = os.path.join(self.movie_dir, movie_file)
                break

        # return if the movie file has not been found
        if not movie_file_path:
            self.logger.error(f"Can not find movie file named {self.pdf_data.shot_name}")
            return

        # define the movie file name
        thumbnail_name = f"{self.pdf_data.shot_name}_thumbnail.png"
        thumbnail_path = self.get_temp_file_path(thumbnail_name)
        self.logger.info(f"Saved: {thumbnail_path}")

        # extract the thumbnail from the movie file
        command = (f"{FFMPEG_EXE} -y -i {movie_file_path} -frames:v 1 "
                   f"-s {THUMBNAIL_SIZE} {self.pdf_data.thumbnail_path}")
        self.run_ffmpeg_command(command)
        self.created_message(thumbnail_path)

        # if the thumbnail exists then use that
        if os.path.exists(thumbnail_path):
            self.pdf_data.thumbnail_path = thumbnail_path

    def created_message(self, path):
        # type: (str) -> None
        """
        Give the created message if the file exists

        Args:
            path: Path of the file to check exists
        """
        if os.path.exists(path):
            self.logger.info(f"Created thumbnail: {path}")
        else:
            self.logger.error(f"Failed to create: {path}")

    def get_temp_file_path(self, file_name):
        # type: (str) -> str
        """
        Get a temp file path with the file name

        Args:
            file_name: Name of the file to create

        Returns:
            The full file path to create
        """
        return os.path.join(tempfile.gettempdir(), file_name)

    def create_slate(self, pdf_data, output_dir):
        # type: (str, str) -> None
        """
        Create the finished slate with the thumbnail and text

        Args:
            pdf_data: The data of the slate to make
            output_dir: The output directory of the slates
        """
        self.logger.info("")
        self.logger.info(f"Shot name: {pdf_data.shot_name}")

        # create the overlay image
        temp_image_overlay_path = self.get_temp_file_path(f"{pdf_data.shot_name}_slate.png")
        command = (f'{FFMPEG_EXE} -y -i {BLANK_SLATE} -i {pdf_data.thumbnail_path} '
                   f'-filter_complex "overlay=1100:170" {temp_image_overlay_path}')
        self.run_ffmpeg_command(command)
        self.created_message(temp_image_overlay_path)

        # text in format in year, day, month format
        date_string = datetime.datetime.now().strftime("%Y/%d/%m")

        # build the slate shot name
        version_padded = str(int(pdf_data.version)).zfill(4)
        slate_shot_name = f"{pdf_data.shot_name}_pstv_c{version_padded}"

        # build text args of the display text and x positions
        text_dict = {
            f"Date\: {date_string}": 385,
            f"Show\: {pdf_data.show_name}": 435,
            f"Name\: {slate_shot_name}": 557,
            f"Resolution\: {pdf_data.resolution}": 652,
            f"Version\: {pdf_data.version}": 702,
            f"Lens\: {pdf_data.focal_length}": 752,
            f"Duration\: {pdf_data.duration}": 802,
            f"Note\: {pdf_data.notes}": 852,
        }

        # get the output file path
        finished_slate_path = os.path.join(output_dir, f"{pdf_data.shot_name}_slate.png")

        # build a list of the arguments of the overlay text
        text_args = list()
        for text, ypos in text_dict.items():
            text_argument = TEXT_FORMAT.format(DRIVE_LETTER=DRIVE_LETTER, NO_DRIVE_PATH=NO_DRIVE_PATH, text=text, ypos=ypos, font_size=FONT_SIZE)
            text_args.append(text_argument)

        # build the ffmpeg command to create the finished slate
        full_text_cmd = ",".join(text_args)
        command = f'{FFMPEG_EXE} -y -i {temp_image_overlay_path} -vf "{full_text_cmd}" {finished_slate_path}'
        self.run_ffmpeg_command(command)
        self.created_message(finished_slate_path)

        # log the final output
        self.logger.info(f"Created slate: {finished_slate_path}")
