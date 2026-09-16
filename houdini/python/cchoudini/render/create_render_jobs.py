""" Create render jobs to run on the farm """
import os
import cchoudini.utils.hou_utils as hou_utils
import cccore.deadline.submit as submit
import cccore.data.server_data as server_data
import cccore.utils.file_utils as file_utils
import cccore.utils.sequence_utils as sequence_utils
from typing import Optional


def create_ass_job(
        deadline_node,  # type: hou.Node
        ass_frame_range,  # type: str
        data_file_path,  # type: str
        prefix,  # type: str
        chunk_size=None,  # type: Optional[int]
        priority=None,  # type: Optional[int]
        username=None,  # type: Optional[str]
        arnold_rops=None,  # type: Optional[str]
    ):
    """
    Create generate the ass file job

    Args:
        deadline_node: Houdini node used to submit to Deadline
        ass_frame_range: The frame range in string
        data_file_path: Metadata file path
        prefix: Farm prefix for the batch name
        chunk_size: Number of chunks
        priority: The job priority
        username: Name of the artist submitting
        arnold_rops: String of arnold rops

    Returns:
        gen_ass_job: The deadline job to submit
    """
    project_data = server_data.ProjectData()
    ass_exporter_py = "houdini/python/cchoudini/exporter/ass_exporter.py"
    ass_exporter_path = project_data.get_relative_path(ass_exporter_py)

    # add node names to the job name
    if not arnold_rops:
        rops = hou_utils.input_nodes_of_type(deadline_node, ["arnold"])
        arnold_rops = ", ".join([rop.name() for rop in rops])
    job_name = f"Ass Generate: {arnold_rops} - {ass_frame_range}"

    chunk_size = chunk_size or 10
    priority = priority or 50

    # create submit dictionary
    custom_dict = {
        "prefix": prefix
    }

    job_info_dict = {
        "Name": job_name,
        "ChunkSize": chunk_size,
        "Pool": "h_batch",
        "Priority": priority,
        "Frames": ass_frame_range
    }
    if username:
        job_info_dict["UserName"] = username

    plugin_info_dict = {
        "Arguments": data_file_path,
        "PythonFile": ass_exporter_path
    }

    gen_ass_job = submit.AssGenDeadlineSubmit(
        job_info_dict,
        plugin_info_dict,
        custom_dict
    )
    return gen_ass_job


def create_arnold_job(arnold_rop, ass_job_id, batch_name, prefix, username=None):
    # type: (hou.Node, str, str, str, str, Optional[str]) -> submit.ArnoldDeadlineSubmit
    """
    Create arnold to kick the ass file and create render

    Args:
        arnold_rop: Houdini arnold node to render
        ass_job_id: The ass deadline job id
        batch_name: Name of the batch group to parent under
        prefix: Farm prefix for the batch name
        username: Name of the artist submitting

    Returns:
        gen_ass_job: The deadline job to submit
    """
    start, end = hou_utils.get_frame_range(arnold_rop)
    frame_range = f"{start}-{end}"

    rop_name = arnold_rop.name()
    ass_path = arnold_rop.parm("ar_ass_file").eval()

    # save sequences
    output_path = arnold_rop.parm("ar_picture").eval()

    # get output path information
    output_dir = os.path.dirname(output_path)
    file_utils.create_directories(output_dir)

    output_sequence = sequence_utils.convert_frame_to_sequence(output_path)
    plugin_info_dict = {
        "InputFile": ass_path,
        "FrameRange": frame_range
    }

    # create jobs directory
    job_info_dict = {
        "OutputDirectory0": os.path.dirname(output_sequence),
        "OutputFilename0": os.path.basename(output_sequence),
        "AddEnvironment": False,
        "IsFrameDependent": True,
        "ChunkSize": 1,
        "Frames": frame_range,
        "Pool": "houdini",
        "Priority": 50,
    }
    if username:
        job_info_dict["UserName"] = username

    # create submit dictionary
    custom_dict = {
        "prefix": prefix
    }

    job_name = f"Arnold Node: {rop_name} - {frame_range}"
    job_info_dict["Name"] = job_name

    arnold_job = submit.ArnoldDeadlineSubmit(
        job_info_dict,
        plugin_info_dict,
        custom_dict
    )

    # add as a dependency to the main job
    arnold_job.add_dependencies(ass_job_id, batch_name)
    return arnold_job


def create_publish_job(prefix, data_file_path, job_ids, batch_name, username=None):
    # type: (str, str, list[str], str, Optional[str]) -> submit.FTrackPublishDeadlineSubmit
    """
    Create ftrack publish job

    Args:
        prefix: Farm prefix for the batch name
        data_file_path: Metadata file path
        job_ids: List of deadline ids to add as dependencies
        batch_name: Name of the batch group to parent under
        username: Name of the artist submitting

    Returns:
        publish_job: The ftrack publish deadline job to submit
    """
    job_info_dict = {
        "Name": prefix + " (Arnold Render)",
        "DefaultPythonHome": True,
        "AddSlackNotification": True
    }
    if username:
        job_info_dict["UserName"] = username

    plugin_info_dict = {
        "DataFilePath": data_file_path
    }

    # create submit dictionary
    custom_dict = {
        "prefix": prefix
    }

    publish_job = submit.FTrackPublishDeadlineSubmit(
        job_info_dict,
        plugin_info_dict,
        custom_dict
    )
    publish_job.add_dependencies(job_ids, batch_name)
    return publish_job

