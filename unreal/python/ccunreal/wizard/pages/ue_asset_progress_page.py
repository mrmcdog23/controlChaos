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

    def export_skeletal_mesh(self, asset_path, out_file):
        #unreal.log_warning(f"loading... {dir(asset_path)}")
        mesh = unreal.EditorAssetLibrary.load_asset(asset_path.get_path_name())
        if not isinstance(mesh, unreal.SkeletalMesh):
            unreal.log_error(f"{asset_path} is not a SkeletalMesh")
            return False

        # FBX export settings
        options = unreal.FbxExportOption()
        options.vertex_color = True
        options.level_of_detail = False   # export only LOD0
        options.collision = False

        task = unreal.AssetExportTask()
        task.object = mesh
        task.filename = out_file          # e.g. "C:/Exports/SK_Hero.fbx"
        task.automated = True             # suppress dialogs
        task.prompt = False
        task.replace_identical = True
        task.options = options

        return unreal.Exporter.run_asset_export_task(task)



    def batch_export(self):
        print ("test")
        selected = self.wizard().selected
        print (selected)
        asset_path = selected[0]


        cleanup_asset_exporter = "C:/Users/joele/Documents/Code/controlChaos/maya/python/ccmaya/wizard/exporter/cleanup_asset_exporter.py"
        path = ["C:/Users/joele/Documents/Code/controlChaos/maya/python/ccmaya/wizard/exporter/cleanup_asset_exporter.py", "cubt"]
        ue_app_version = os.environ.get("APP_VERSION")
        os.environ["APP_VERSION"] = "2025"
        output_path = "C:/Users/joele/Downloads/test/testing.txt"
        fbx_file_path = "C:/Users/joele/Downloads/test/testiddng.fbx"
        file_name = file_utils.get_file_name(fbx_file_path)
        self.export_skeletal_mesh(asset_path, fbx_file_path)

        pipeline_root = os.environ["PIPELINE_ROOT"]
        os.environ["PYTHONPATH"] += f";{pipeline_root}/maya/python"

        data = {"fbx_file_path": fbx_file_path}
        temp_json_path = file_utils.temp_file_path(file_name, "json")
        file_utils.write_file(temp_json_path, data)

        self.progress_wdg.start_maya_process([cleanup_asset_exporter, temp_json_path], output_path=output_path)
        os.environ["APP_VERSION"] = ue_app_version

