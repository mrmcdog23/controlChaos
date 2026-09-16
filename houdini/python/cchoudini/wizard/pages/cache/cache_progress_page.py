""" Submit caches to the farm progress page """
import hou
from typing import Optional
import cccore.deadline.submit as submit
import cccore.utils.file_utils as file_utils
import cccore.data.server_data as server_data
import cccore.core_constants as core_constants
from cchoudini.node.cccache import No8CacheNode
from cchoudini.node.ccwedger import No8WedgerNode
from cchoudini.wizard.pages.hou_progress_page import ProgressPage


CACHE_EXPORTER = "houdini/python/cchoudini/exporter/cache_exporter.py"
FTRACK_PUBLISH = core_constants.FTRACK_PUBLISH


class CacheProgressPage(ProgressPage):
    title = "Houdini Progress Page"
    subtitle = "Submitting Arnold Nodes"

    def __init__(self, parent=None):
        super(CacheProgressPage, self).__init__(parent)
        self.batch_name = str()
        self.cache_name = str()
        self.cccache_inst = None
        self.cc_cache_node = None
        self.cc_wedger_node = None
        self.wedger_cache_paths = list()

        # set class variables
        self.prefix = str()
        self.metadata_path = str()
        self.custom_dict = dict()
        self.cache_job_id = str()
        self.cache_job = None

    def deadline_export(self):
        """
        Submit the cache to deadline
        """
        hou.hipFile.save()

        # set progress
        self.add_message("Submitting cache to Deadline...")
        self.set_value(20)

        self.cc_cache_node = self.wizard().node
        self.cccache_inst = No8CacheNode(self.cc_cache_node)
        self.cache_name = self.cc_cache_node.parm("cache_name").eval()

        # if it is a wedger input then set the values and submit individually
        self.cc_wedger_node = self.cccache_inst.cc_wedger_node
        if self.cc_wedger_node:
            self.submit_wedges()
        else:
            self.submit_cache()

        self.publish_cache()

        # complete process
        self.add_message("Submitted!")
        self.process_finished()

    def submit_wedges(self):
        """
        Submit the individual wedges to the farm
        """
        ccwedger_inst = No8WedgerNode(self.cc_wedger_node)
        for wedge_index, parm_name in enumerate(ccwedger_inst.parms_names_to_submit, start=1):
            wedge_value = ccwedger_inst.set_node_to_wedge(parm_name)
            self.data["wedge_value"] = wedge_value

            # update cccache node for wedge name to get the output path
            new_cache_name = f"{self.cache_name}_wedge{wedge_index}"
            self.data["new_cache_name"] = new_cache_name
            self.cc_cache_node.parm("cache_name").set(new_cache_name)

            # add to the list of wedger paths
            wedger_cache_path = self.cc_cache_node.parm("output_path").eval()
            self.wedger_cache_paths.append(wedger_cache_path)

            suffix = f" wedge{wedge_index}"
            self.submit_cache(suffix=suffix)

        # reset to original value
        self.cc_cache_node.parm("cache_name").set(self.cache_name)

    def submit_cache(self, suffix=None):
        # type: (Optional[str]) -> None
        """
        Submit a cache with the current settings
        """
        self.cccache_inst = No8CacheNode(self.cc_cache_node)

        # save the file metadata
        node_data, self.metadata_path = self.cccache_inst.save_metadata(data=self.data)

        project_data = server_data.ProjectData()
        task_structure_path = project_data.get_relative_path(CACHE_EXPORTER)

        # build submit to the farm dictionaries
        wip_file_path = hou.hipFile.name()
        self.prefix = file_utils.get_file_name(wip_file_path)
        self.custom_dict = {"prefix": self.prefix}

        if self.batch_name:
            self.custom_dict["batch_name"] = self.batch_name

        # build submit to the farm dictionaries
        cache_type = self.cccache_inst.get_cache_type()
        frame_range = "{}-{}".format(int(node_data["start"]),
                                     int(node_data["end"])
                                     )

        # create the job dictionary
        job_name = f"Cache Node: {self.cc_cache_node.name()} {frame_range} ({cache_type})"
        if suffix:
            job_name += suffix

        job_info_dict = {"Name": job_name,
                         "Pool": self.data["pool"],
                         "AddSlackNotification": False
                         }

        # if it is a bgeo or vdb use the frames and chunk size
        if cache_type != "abc":
            number_of_chunks = file_utils.get_number_of_chunks(
                self.data["start"], self.data["end"], self.data["chunk_size"])
            job_info_dict["Frames"] = frame_range
            job_info_dict["ChunkSize"] = number_of_chunks

        plugin_info_dict = {"Arguments": self.metadata_path,
                            "PythonFile": task_structure_path
                            }

        # submit the houdini job to the farm
        submit_cls_dict = {"abc": submit.AbcCachePyDeadlineSubmit,
                           "bgeo": submit.BGeoCachePyDeadlineSubmit,
                           "vdb": submit.VDBCachePyDeadlineSubmit,
                           "fbx": submit.FBXCachePyDeadlineSubmit
                           }
        submit_cls = submit_cls_dict[cache_type]
        self.cache_job = submit_cls(
            job_info_dict,
            plugin_info_dict,
            self.custom_dict
        )
        self.cache_job_id = self.cache_job.submit_job()

        # set the batch name
        if not self.batch_name:
            self.batch_name = self.cache_job.batch_name
        self.add_submit_data(self.cache_job_id, cache_type)

    def publish_cache(self):
        """
        Publish the caches to ftrack via Deadline job
        """
        # tag on publish job
        if not self.data["publish"]:
            return

        # if the wedger has been run update
        # the metadata to include all caches
        if self.wedger_cache_paths:
            data = file_utils.read_json(self.metadata_path)
            data["file_sequences"] = self.wedger_cache_paths
            file_utils.write_json(self.metadata_path, data)

        # if publish then create the publish
        # job once all other jobs have finished
        job_info_dict = {"Name": self.prefix + " (Publish)",
                         "DefaultPythonHome": True
                         }

        plugin_info_dict = {"DataFilePath": self.metadata_path}
        publish_job = submit.FTrackPublishDeadlineSubmit(job_info_dict,
                                                         plugin_info_dict,
                                                         self.custom_dict
                                                         )
        publish_job.add_dependencies(self.cache_job_id, self.cache_job.batch_name)
        publish_id = publish_job.submit_job()
        self.add_submit_data(publish_id, self.FTRACK_PUBLISH)
