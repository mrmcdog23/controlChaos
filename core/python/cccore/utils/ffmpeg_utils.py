""" Run ffmpeg functions """
import os
import subprocess
import cccore.utils.cc_logging as cc_logging
import cccore.core_constants as core_constants


logger = cc_logging.cc_logger()


FFMPEG_FNT = '{ffmpeg_exe} -s 640x480 -nostdin -start_number {start} -i "{path}" "{mov_path}"'
CONVERT_TO_MOV = '{ffmpeg_exe} -i "{mov_path}" -vf "{args}" -loop 10 "{gif_path}"'
GIF_ARGS = "fps=25,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
CONVERT_IMAGE_TYPE = '{ffmpeg_exe} -i "{input_path}" {resize_cmd} "{output_path}"'


def run_ffmpeg_hud_command(start, nuke_path, mov_path):
    # type: (int, str, str) -> bool
    """
    Build the hud command to go over the renders on shot publish

    Args:
        start: First frame of the sequence
        nuke_path: Base name of the sequence
        mov_path: Path of the mov to save

    Returns:
        Has the mov been run successfully
    """
    # build the text to overlay
    # get the image path and extension from the first image
    mov_path = mov_path.replace("\\", "/")
    if os.path.exists(mov_path):
        os.remove(mov_path)

    ffmpeg_slate_command = FFMPEG_FNT.format(
        ffmpeg_exe=core_constants.FFMPEG_EXE,
        start=start,
        path=nuke_path,
        mov_path=mov_path
    )
    success = run_ffmpeg_command(ffmpeg_slate_command, mov_path)
    return success


def run_ffmpeg_command(ffmpeg_command, output_path):
    # type: (str, str) -> bool
    """
    Run the ffmpeg command and return if successful

    Args:
        ffmpeg_command: The command to run
        output_path: Path of the output file

    Returns:
        Has the mov been run successfully
    """
    logger.info(f"Command: {ffmpeg_command}")
    process = subprocess.Popen(
        ffmpeg_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )
    process.communicate()
    if os.path.exists(output_path):
        logger.info("Generated ffmpeg file")
        return True
    else:
        logger.error("Failed to generate ffmpeg file")
        return False


def run_ffmpeg_mov_to_gif_command(mov_path, gif_path):
    # type: (str, str) -> bool
    """
    Convert a mov file to gif file

    Args:
        mov_path: Source movie file path
        gif_path: Path of the gif to save

    Returns:
        Has the mov been run successfully
    """
    # build the text to overlay
    # get the image path and extension from the first image
    mov_path = mov_path.replace("\\", "/")
    gif_path = gif_path.replace("\\", "/")
    ffmpeg_gif_command = CONVERT_TO_MOV.format(
        ffmpeg_exe=core_constants.FFMPEG_EXE,
        mov_path=mov_path,
        args=GIF_ARGS,
        gif_path=gif_path
    )
    success = run_ffmpeg_command(ffmpeg_gif_command, gif_path)
    return success


def convert_image_type(input_path, output_path, low_res=False):
    # type: (str, str, bool) -> None
    """
    Convert an image to another image type

    Args:
        input_path: Source file
        output_path: File to create
        low_res: Down res the image
    """
    resize_cmd = " -s 640x480 " if low_res else str()
    ffmpeg_convert_command = CONVERT_IMAGE_TYPE.format(
        ffmpeg_exe=core_constants.FFMPEG_EXE,
        input_path=input_path,
        resize_cmd=resize_cmd,
        output_path=output_path,
    )
    success = run_ffmpeg_command(ffmpeg_convert_command, output_path)
    logger.info(f"Command: {ffmpeg_convert_command}")
    return success
