""" Asset publisher in maya """
import os
import sys
import maya.cmds as cmds
import cccore.utils.file_utils as file_utils
import cccore.core_constants as core_constants
import ccmaya.utils.maya_utils as maya_utils
import ccmaya.maya_constants as maya_constants
import cccore.file_env.context as context
import ccmaya.asset.fbx_asset_export as fbx_asset_export
import cccore.file_env.ctx_constants as ctx_constants
from ccgeneral.wizard.exporter.base_exporter import BaseExporter


# initialize maya standalone
try:
    import maya.standalone
    maya.standalone.initialize()
except (TypeError, RuntimeError):
    pass


class AssetExporter(BaseExporter):
    def __init__(self):
        super(AssetExporter, self).__init__()
        self.asset_data = dict()
        self.asset_version_id = None
        self.ctx = None

    def export(self):
        """
        Export the asset and publish it to ftrack
        """
        self.export_clean_asset()

        self.create_asset_version()
        self.add_progress(10)

        self.tag_and_copy_asset_version()
        self.add_progress(10)

        # write the data out
        self.create_alembic_component()
        self.add_progress(10)

        self.create_usd_component()
        self.add_progress(10)

        #self.create_asset_metadata()
        self.add_progress(10)

        #self.create_materialx_file()
        self.add_progress(10)

        self.export_fbx_unreal_component()
        self.add_progress(10)
        self.log("Asset publish complete")

    def open_file(self):
        """
        Load the alembic export plugin and open the maya file
        """
        maya_utils.load_plugins(["AbcExport"])
        cmds.file(self.data['wip_file_path'],  open=True, force=True)

    def create_asset_version(self):
        """
        Create the asset version on ftrack and get publish path
        """
        self.data["entity"] = ctx_constants.BUILD
        self.data["ext"] = "ma"
        self.ctx = context.Context(overrides=self.data)

        # work out the next version to publish
        self.next_version = self.ftquery.next_version_from_ctx(self.ctx)
        self.ctx.use_version = self.next_version
        self.logger.info(f"Using next version number: {self.next_version}")

        # set the ftrack data
        self.asset_version = self.ftasset.set_ftrack_data(self.data)

        # publish the file to ftrack
        self.log("Publishing asset to FTrack...")
        asset_version_id = self.asset_version["id"]
        message = f"{core_constants.VERSION_TEXT} {asset_version_id}"
        self.log(message)

        # set page completed
        self.ftver.asset_version_id = asset_version_id

    @property
    def is_camera(self):
        # type: () -> str
        """ Is it a camera publish asset """
        return self.data["asset_build_type_name"] == "Camera"

    def export_clean_asset(self):
        """
        Export the asset and reopen the file to
        not have any unwanted nodes in there
        """
        if self.is_camera:
            return

        maya_utils.load_plugins(["fbxmaya"])
        top_nodes = maya_utils.get_top_level_nodes()
        if len(top_nodes) == 1:
            self.logger.info("Only one top node found...")
            return

        self.logger.info("Exporting as more than one top node found...")
        top_node = maya_utils.get_asset_top_node()
        cmds.select(top_node)
        temp_lookdev_path = file_utils.join_from_list(
            self.project_data.appdata, "temp_asset_export.ma")

        self.log(f"temp asset path: {temp_lookdev_path}")
        cmds.file(temp_lookdev_path, force=True, pr=True, es=True, typ="mayaAscii")
        cmds.file(temp_lookdev_path, open=True, force=True)

    def tag_and_copy_asset_version(self):
        """
        Create the ftrack publish version and
        add the id to the top level node
        """
        # add tag to the asset attribute
        maya_utils.add_ftrack_tag_to_asset(self.asset_version['id'])

    def create_alembic_component(self):
        """
        Alembic export args. These vary on the object type to cache
        """
        if self.data["asset_build_type_name"] == "Camera":
            abc_export_args = " ".join(maya_constants.CAM_ABC_ARGS)
            root = maya_constants.CAM_GRP
        else:
            abc_export_args = " ".join(maya_constants.MESH_ABC_ARGS)
            root = maya_constants.GEO_GRP

        # get alembic path from publish path
        abc_path = self.ctx.alembic_file_path

        # create alembic directory
        file_utils.create_directories(os.path.dirname(abc_path))

        # export alembic
        abc_args = maya_constants.JOB_ARGS_FORMAT.format(
            step=1,
            start=1,
            end=2,
            args=abc_export_args,
            root=root,
            path=abc_path
        )
        self.log(f"Alembic Command: {abc_args}")
        cmds.AbcExport(j=abc_args, verbose=True)
        component_dict = {"Alembic": abc_path}
        self.ftver.add_component_dict(component_dict)

    def export_fbx_unreal_component(self):
        """
        Export the unreal asset
        """
        if self.data["task_name"] not in ["modeling", "rigging"]:
            self.log(f"Not a model or rig for Unreal")
            return

        # do not publish fbx camera
        if self.is_camera:
            return

        fbx_asset_path = self.ctx.fbx_file_path
        self.ftver.add_component_dict({"FBX": fbx_asset_path})
        self.log(f"Export FBX path: {fbx_asset_path}")
        fbx_asset_export.FbxAssetExport(fbx_asset_path)

    def create_usd_component(self):
        """
        Create the usd file and component
        """
        # get usd path from publish path
        usd_file_path = self.ctx.usd_file_path

        # export the file
        cmds.file(
            usd_file_path,
            force=True,
            options="-mask 6399;-lightLinks 1;-shadowLinks 1;-fullPath",
            type="Arnold-USD",
            pr=True,
            ea=True
        )
        self.log(f"Exported usd file: {usd_file_path}")
        component_dict = {"USD": usd_file_path}
        self.ftver.add_component_dict(component_dict)

    def get_save_file_path(self, extension):
        # type: (str) -> str
        """
        Get the save file path by taking the published file
        path and replacing the extension with the given one

        Args:
            extension: New file extension to use

        Returns:
            save_file_path: Path of the file to save
        """
        wip_file_path = self.ftasset.data["wip_file_path"]
        wip_file_path_no_ext, _ = os.path.splitext(wip_file_path)
        save_file_path = f"{wip_file_path_no_ext}.{extension}"
        return save_file_path

    def create_asset_metadata(self):
        """
        Create and save asset metadata
        """
        asset_metadata_path = self.get_save_file_path("json")
        asset_data = {
            "material_name_to_type": self.material_name_to_type,
            "mesh_to_materials": self.mesh_to_materials
        }
        file_utils.write_json(asset_metadata_path, asset_data)
        component_dict = {"Metadata": asset_metadata_path}
        self.ftver.add_component_dict(component_dict)

    def create_materialx_file(self):
        """
        If there is geometry save a materialx file path
        """
        if not cmds.objExists(maya_constants.GEO_GRP):
            return
        cmds.select(maya_constants.GEO_GRP)
        materialx_path = self.get_save_file_path("mtlx")
        look_name = self.data["asset_build_name"]
        cmds.arnoldExportToMaterialX(
            filename=materialx_path,
            look=look_name,
            relative=True,
            fullPath=True,
            separator="/"
        )
        component_dict = {"MaterialX": materialx_path}
        self.ftver.add_component_dict(component_dict)

    @property
    def material_name_to_type(self):
        # type: () -> dict
        """ Build dictionary of material name to its type """
        material_name_to_type = dict()
        for material in cmds.ls():
            material_name_to_type[material] = cmds.objectType(material)
        return material_name_to_type

    @property
    def mesh_to_materials(self):
        # type: () -> dict
        """ Dictionary of mesh path to its material name """
        top_node = maya_utils.get_asset_top_node()
        mesh_to_materials = dict()
        all_meshes = cmds.listRelatives(top_node, ad=True, f=True, type="mesh")
        if not all_meshes:
            return mesh_to_materials

        for mesh in all_meshes:
            try:
                sg = cmds.listConnections(mesh, type="shadingEngine")[0]
            except (IndexError, TypeError):
                continue
            sg_attribute = f"{sg}.surfaceShader"
            shader = cmds.listConnections(sg_attribute)[0]
            mesh_to_materials[mesh] = shader
        return mesh_to_materials


if __name__ == "__main__":
    exporter = AssetExporter()
    exporter.batch_process(sys.argv[1])
