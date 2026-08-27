""" Maya shot exporter for publishing scenes """
import os
import sys
import maya.cmds as cmds
import maya.mel as mel
import cccore.utils.file_utils as file_utils
import ccmaya.maya_constants as maya_constants
import ccmaya.asset.scene_asset as scene_asset
import ccmaya.utils.maya_utils as maya_utils
import cccore.file_env.context as context
import ccftrack.publish as publish
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
        self.ctx = None
        self.exported_files_to_data = dict()
        self.additional_components = dict()

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
        self.publish_shot()
        self.log(f"Export Complete")

    @BaseExporter.add_to_percentage(15)
    def cache_assets(self):
        """
        Cache all the assets in the scene
        """
        self.logger.info("Caching assets...")
        all_namespaces = self.data["namespaces"]

        # set the next version number
        self.ctx = context.Context(self.data)
        self.next_version = self.ftquery.next_version_from_ctx(self.ctx)
        self.logger.info(f"Using next version number: {self.next_version}")

        self.ctx.use_version = self.next_version
        self.abc_version_dir = self.ctx.alembic_file_path

        namespace_to_data = dict()
        for namespace in all_namespaces:
            abc_path = self.abc_export(namespace)
            scene_asset_inst = scene_asset.SceneAsset(namespace)
            self.exported_files_to_data[abc_path] = scene_asset_inst.asset_data_dict

            # store the namespace data to be reused for the fbx files
            namespace_to_data[namespace] = scene_asset_inst.asset_data_dict

        # run the fbx export separately
        fbx_inst = fbx_anim_export.FbxAnimExport(all_namespaces, self.ctx)
        fbx_inst.run_fbx_exports()

        # add the fbx paths to the exported files dictionary
        for namespace, fbx_path in fbx_inst.namespace_to_fbx_path.items():
            self.exported_files_to_data[fbx_path] = namespace_to_data[namespace]

            # add fbx namespace to additional dictionary
            self.additional_components[f"fbx_{namespace}"] = fbx_path

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

        self.ctx.use_suffix = namespace
        abc_path = self.ctx.alembic_file_path

        file_utils.create_directories(os.path.dirname(abc_path))
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

        # add namespace to additional dictionary
        self.additional_components[f"abc_{namespace}"] = abc_path
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
        # update and save all metadata
        data = {
            "exported_files_to_data": self.exported_files_to_data,
            "start_frame": int(cmds.playbackOptions(q=True, min=True)),
            "end_frame": int(cmds.playbackOptions(q=True, max=True)),
            "master_scene": cmds.file(q=True, sn=True)
        }
        data.update(self.data)

        self.ctx.use_suffix = "metadata"
        data_file_path = self.ctx.data_file_path
        self.logger.info(f"Writing metadata: {data_file_path}")
        file_utils.create_directories(os.path.dirname(data_file_path))
        file_utils.write_file(data_file_path, data)

        # add the data to the dictionary
        self.additional_components["metadata"] = data_file_path

    @BaseExporter.add_to_percentage(10)
    def publish_shot(self):
        """
        Publish the shot to ftrack
        """
        self.data["additional_components"] = self.additional_components
        publish_inst = publish.FtrackPublish(self.data)
        self.asset_version = publish_inst.asset_version
        asset_version_id = self.asset_version["id"]
        self.ftver.asset_version_id = asset_version_id
        self.log(f"Asset Version: {asset_version_id}")


if __name__ == "__main__":
    exporter = ShotExporter()
    exporter.batch_process(sys.argv[1])
