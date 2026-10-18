""" Maya specific progress page """
import re
import os
import unreal
from typing import Optional
from ccgeneral.wizard.pages.progress_page import ProgressPage
import cccore.utils.file_utils as file_utils


class UEAssetProgressPage(ProgressPage):
    title = "Unreal Asset Progress Page"
    subtitle = "Exporting the shot asset"

    def __init__(self, parent=None):
        super().__init__(parent)

    def export_skeletal_mesh(self, asset_path, fbx_file_path):
        """
        Export the skeletal mesh as a fbx file

        Args:
            asset_path: Path of the skeletal mesh
            fbx_file_path: The path to export the fbx to
        """
        mesh = unreal.EditorAssetLibrary.load_asset(asset_path)
        if isinstance(mesh, unreal.SkeletalMesh):
            self.data["task_name"] = "rigging"

        if isinstance(mesh, unreal.StaticMesh):
            self.data["task_name"] = "modeling"

        # FBX export settings
        options = unreal.FbxExportOption()
        options.vertex_color = True
        options.level_of_detail = False   # export only LOD0
        options.collision = False

        # export task settings
        task = unreal.AssetExportTask()
        task.object = mesh
        task.filename = fbx_file_path     # e.g. "C:/Exports/SK_Hero.fbx"
        task.automated = True             # suppress dialogs
        task.prompt = False
        task.replace_identical = True
        task.options = options
        return unreal.Exporter.run_asset_export_task(task)

    def batch_export(self):
        """
        Run the batch export task
        """
        selected = self.wizard().selected
        asset_path = selected[0].get_path_name()

        # build the relevant temp file paths
        temp_json_path = file_utils.temp_file_path("asset_export", "json")
        fbx_file_path = temp_json_path.replace(".json", ".fbx")
        #output_path = temp_json_path.replace(".json", ".txt")
        output_path = "C:/Users/joele/Downloads/rlling.txt"

        # export the skeletal mesh as an fbx file
        self.export_skeletal_mesh(asset_path, fbx_file_path)

        self.data["fbx_file_path"] = fbx_file_path
        file_utils.write_file(temp_json_path, self.data)

        # add maya to the python paths
        pipeline_root = os.environ["PIPELINE_ROOT"]
        os.environ["PYTHONPATH"] += f";{pipeline_root}/maya/python"

        # store the current app version then use the maya version
        ue_app_version = os.environ.get("APP_VERSION")
        os.environ["APP_VERSION"] = "2025"

        # run the fbx clean up process
        cleanup_asset_exporter = self.project_data.get_relative_path(
            "maya/python/ccmaya/wizard/exporter/cleanup_asset_exporter.py")

        self.progress_wdg.start_maya_process(
            [cleanup_asset_exporter, temp_json_path], output_path=output_path)

        # switch back to the original version
        os.environ["APP_VERSION"] = ue_app_version

