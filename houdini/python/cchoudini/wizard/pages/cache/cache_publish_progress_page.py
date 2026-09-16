""" Submit caches to publish the farm progress page """
import os
import hou
import htoa.material as mat
import cccore.utils.ass_materials as ass_materials
import cccore.deadline.submit as submit
import cccore.utils.file_utils as file_utils
import cccore.file_env.context_utils as context_utils
import ccftrack.publish as publish
import cchoudini.utils.hou_utils as hou_utils
from cchoudini.wizard.pages.hou_progress_page import HouProgressPage


RIG_EXPORTER = "maya/python/ccmaya/exporter/rig_create_exporter.py"


class CachePublishProgressPage(HouProgressPage):
    title = "Houdini Progress Page"
    subtitle = "Submitting Cache To Publish"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.prefix = str()
        self.metadata_path = str()
        self.custom_dict = dict()
        self.publish_id = str()
        self.maya_job_id = str()
        self.batch_name = str()

    def save_material_description(self):
        """
        Save the materials as a matdesc file that
        is an ass file with its own extension
        """
        self.add_message("Saving material file...")
        cc_cache_node = self.wizard().node

        # get and loop through all materials
        vops = list()
        materials = hou_utils.input_nodes_of_type(
            cc_cache_node, node_type_names=["material"])
        for material in materials:
            material_path = material.parm("shop_materialpath1").eval()
            material_node = hou.node(material_path)

            # add material to list
            if material_node.type().name() in ['arnold_materialbuilder', 'arnold_vopnet']:
                vops.append(material_node)

        # save material data as an ass file
        ass_file_path = file_utils.temp_file_path("material_ass", "ass")
        self.add_message(f"Temp ass file: {ass_file_path}")
        mat.materialExport(vops, ass_file_path)

        # get save path
        ctx = context_utils.get_context_from_path(self.output_path)
        ctx.use_subfolder = "archive"
        ctx.use_ext = "matdesc"
        matdesc_file_path = ctx.wip_file_path
        file_utils.create_directories(os.path.dirname(ass_file_path))

        # convert ass to json file
        material_data = ass_materials.convert_ass_to_data(ass_file_path)
        file_utils.write_json(matdesc_file_path, material_data)
        self.add_message(f"Material description path: {matdesc_file_path}")
        self.data["additional_components"] = {"MaterialDescription": matdesc_file_path}

    @property
    def version_num(self):
        # type: () -> str
        """ The file version number """
        cc_cache_node = self.wizard().node
        return cc_cache_node.parm("version").evalAsString()

    @property
    def output_path(self):
        # type: () -> str
        """ The file output path """
        cc_cache_node = self.wizard().node
        return cc_cache_node.parm("output_path").evalAsString()

    def update_cache_data(self):
        """
        Get the information from the cache node and update the data
        """
        self.data["file_sequences"] = [self.output_path]
        self.data["category"] = "Cache"

    def batch_export(self):
        """
        Export the asset version in batch mode
        """
        self.update_cache_data()
        self.save_material_description()

        self.add_message("Publishing to FTrack...")
        ftrack_pub_inst = publish.FtrackPublish(self.data)
        asset_version_id = ftrack_pub_inst.asset_version["id"]
        self.add_message(f"Asset Version: {asset_version_id}")
        self.process_finished()

    def create_maya_components(self):
        """
        If it is an alembic file then create an alembic
        """
        if not self.output_path.endswith(".abc"):
            return

        # submit the maya job
        job_info_dict = {
            "Name": f"{self.prefix} (Rig Creator)",
            "Pool": self.data.get("pool"),
            "Priority": self.data.get("priority")
        }
        plugin_info_dict = {
            "ScriptFile": self.project_data.get_relative_path(RIG_EXPORTER),
            "Arguments": self.metadata_path
        }
        python_path = os.environ["PYTHONPATH"]
        maya_python = self.project_data.get_relative_path("maya/python")
        new_python_path = f"{maya_python}:/usr/autodesk/maya2025/lib/python3.11/site-packages/:{python_path}"
        additional_env = {"PYTHONPATH": new_python_path}
        custom_dict = {
            "prefix": self.prefix,
            "additional_env": additional_env
        }
        maya_job = submit.MayaPyDeadlineSubmit(
            job_info_dict,
            plugin_info_dict,
            custom_dict
        )
        maya_job.add_dependencies(self.publish_id, self.batch_name)
        maya_job.batch_name = self.batch_name
        maya_job_id = maya_job.submit_job()
        self.add_submit_data(maya_job_id, self.MAYA_PUBLISH)

    def deadline_export(self):
        """
        Submit the cache to deadline
        """
        self.prefix = file_utils.get_file_name(self.output_path)

        # set progress
        self.add_message("Submitting publish to Deadline...")
        self.set_value(50)

        self.update_cache_data()
        self.save_material_description()
        self.metadata_path = self.save_data_to_json()

        # build the job dictionary
        job_info_dict = {
            "Name": f"{self.prefix} (Publish)",
            "DefaultPythonHome": True,
            "Pool": "python"
        }
        # build the plugins dictionary
        plugin_info_dict = {
            "DataFilePath": self.metadata_path
        }

        custom_dict = {"prefix": self.prefix}

        publish_job = submit.FTrackPublishDeadlineSubmit(
            job_info_dict,
            plugin_info_dict,
            custom_dict
        )

        # add the maya rig build as a dependency
        self.publish_id = publish_job.submit_job()
        self.batch_name = publish_job.batch_name
        self.add_submit_data(self.publish_id, self.FTRACK_PUBLISH)

        self.create_maya_components()

        self.add_message("Submitted!")
        self.process_finished()
