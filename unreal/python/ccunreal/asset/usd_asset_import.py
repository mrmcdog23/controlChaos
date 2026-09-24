""" Import fbx asset from asset version """
import re
import os
import unreal as ue
import ccunreal.asset.base_asset_import as base_asset_import


class USDAssetImport(base_asset_import.BaseAssetImport):
    """
    Import a cache asset into the scene
    """
    def __init__(self, source_asset_path, ftver, is_skeleton_mesh):
        super().__init__(source_asset_path, ftver, is_skeleton_mesh)

    def import_asset(self):
        self.set_destination_dir()
        ue.log_warning(f"Importing USD: {self.source_asset_path}")
        ue.log_warning(f"destination_dir: {self.destination_dir}")

        options = ue.UsdStageImportOptions()
        options.import_actors = True
        options.import_geometry = True
        options.import_skeletal_animations = True
        options.import_level_sequences = True
        options.import_materials = True
        options.existing_asset_policy = ue.ReplaceAssetPolicy.REPLACE  # if available in your version

        task = ue.AssetImportTask()
        task.filename = self.source_asset_path
        task.destination_path = self.destination_dir
        task.automated = True  # suppress dialogs
        task.save = True
        task.replace_existing = True
        task.factory = ue.UsdStageImportFactory()
        task.options = options
        ue.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

        print("Imported:", task.imported_object_paths)
        # run post import commands
        self.organize_asset()
        self.save_asset()

