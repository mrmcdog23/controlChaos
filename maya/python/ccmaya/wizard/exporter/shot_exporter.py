""" Maya shot exporter for publishing scenes """
import os
import sys
import maya.cmds as cmds
import maya.mel as mel
import cccore.utils.file_utils as file_utils
import ccmaya.maya_constants as maya_constants
import ccmaya.asset.scene_asset as scene_asset
import ccmaya.utils.maya_utils as maya_utils
import ccmaya.shot.fbx_anim_export as fbx_anim_export
from ccgeneral.wizard.exporter.base_exporter import BaseExporter

# initialize maya standalone
try:
    import maya.standalone
    maya.standalone.initialize()
except (TypeError, RuntimeError):
    pass


class ShotExporter(BaseExporter):
    def __init__(self):
        super().__init__()
        self.save_dir = str()
        self.namespace_to_exported_files = dict()

    @BaseExporter.add_to_percentage(10)
    def open_file(self):
        """
        Open the wip maya file
        """
        maya_utils.load_plugins(["AbcExport"])
        cmds.file(self.data['wip_file_path'],  open=True, force=True)

    def export(self):
        """
        Export the shot assets as fbx and alembic files
        """
        self.cache_assets()
        self.write_metadata()
        self.log(f"Export Complete")

    @BaseExporter.add_to_percentage(15)
    def cache_assets(self):
        """
        Cache all the assets in the scene
        """
        self.logger.info("Caching assets...")
        self.save_dir = self.data["save_dir"]
        namespaces_to_rig = self.data["namespaces_to_rig"]
        all_namespaces = list(namespaces_to_rig.keys())

        for namespace in all_namespaces:
            abc_path = self.abc_export(namespace)
            self.namespace_to_exported_files[namespace] = [abc_path]

        # run the fbx export separately
        fbx_inst = fbx_anim_export.FbxAnimExport(all_namespaces, self.save_dir)
        fbx_inst.run_fbx_exports()

        # add the fbx paths to the exported files dictionary
        for namespace, fbx_path in fbx_inst.namespace_to_fbx_path.items():
            exported_files = self.namespace_to_exported_files[namespace]
            exported_files.append(fbx_path)
            self.namespace_to_exported_files[namespace] = exported_files

    @BaseExporter.add_to_percentage(5)
    def abc_export(self, namespace):
        # type: (str) -> None
        """
        Export scene asset with alembic

        Args:
            namespace: Namespace of asset to cache
        """
        self.logger.info(f"Exporting alembic {namespace}")
        scene_asset_inst = scene_asset.SceneAsset(namespace)

        abc_path = file_utils.join_file_names(self.save_dir, f"{namespace}.abc")
        self.logger.info(f"Alembic path: {abc_path}")

        start = int(cmds.playbackOptions(q=True, min=True))
        end = int(cmds.playbackOptions(q=True, max=True))

        self.logger.info("Build alembic export args...")
        abc_args = maya_constants.JOB_ARGS_FORMAT.format(
            step=1,
            start=start,
            end=end,
            args=scene_asset_inst.abc_export_args,
            root=scene_asset_inst.export_grp,
            path=abc_path
        )
        self.logger.info(f"Export args: {abc_args}")
        cmds.AbcExport(j=abc_args, verbose=True)
        return abc_path

    @BaseExporter.add_to_percentage(5)
    def bake_export_camera(self):
        """
        Bake the cc render camera
        """
        for namespace in self.data["namespaces"]:
            for node in cmds.ls(namespace + ":*"):
                if cmds.objectType(node) != "camera":
                    continue
                transform = cmds.listRelatives(node, p=True)[0]
                relatives = cmds.listRelatives(transform, p=True)
                if relatives:
                    maya_utils.bake_objects_in_world_space(transform)
                    return

    def write_metadata(self):
        """
        Write the metadata json file
        """
        file_name = file_utils.get_file_name(self.data['wip_file_path'])
        metadata_path = file_utils.join_file_names(
            self.save_dir, f"{file_name}_metadata.json")

        # update and save all metadata
        data = {
            "namespace_to_exported_files": self.namespace_to_exported_files,
            "start_frame": int(cmds.playbackOptions(q=True, min=True)),
            "end_frame": int(cmds.playbackOptions(q=True, max=True)),
            "master_scene": cmds.file(q=True, sn=True)
        }
        data.update(self.data)
        file_utils.write_file(metadata_path, data)


if __name__ == "__main__":
    exporter = ShotExporter()
    exporter.batch_process(sys.argv[1])
