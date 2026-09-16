""" Exporter for hda publishing """
import os
import sys
import hou
import cccore.data.server_data as server_data
import cccore.project_creation.write_hou_shelf as write_hou_shelf
from ccgeneral.exporter.base_exporter import BaseExporter
import cchoudini.utils.hou_utils as hou_utils
import cchoudini.utils.node_utils as node_utils


class HDAExporter(BaseExporter):
    """
    Exporter to create and publish a Houdini Digital Asset
    """
    LIB_TASK = "fx"
    LIB_ASSET_TYPE = "otls"
    HDA_FTRACK_ID = "hda_ftrack_id"
    ORIG_ASSET_FTRACK_ID = "orig_asset_ftrack_id"

    def __init__(self):
        super().__init__()
        self.project_data = server_data.ProjectData()
        self.hda_name = None
        self.save_hda_name = None
        self.hda_dest_path = None
        self.definition = None
        self.hda_asset_version_id = None

    def export(self):
        """
        Export the asset and publish it to ftrack
        """
        self.add_progress(20)
        self.hda_name = self.data["asset_build_name"]

        # create asset version on ftrack
        self.create_hda_asset_version()

        # create digital asset
        self.create_digital_asset()

        # write the hda menu
        write_hou_shelf.create_menu()

        # write the data out
        self.log("HDA publish complete..")
        self.finish_exporter_process()

    @property
    def source_node(self):
        # type: () -> hou.Node
        """ The main houdini node """
        return hou.node(self.data["node_path"])

    @property
    def asset_ftrack_id(self):
        # type: () -> str
        """ Ftrack asset id """
        ftrack_id_parm = self.source_node.parm("asset_version_ftrack_id")
        if not ftrack_id_parm:
            return self.get_latest_modeling_asset_id()
        return ftrack_id_parm.evalAsString()

    @property
    def shared_otls_dir(self):
        # type: () -> str
        """ The share otls directory """
        return self.project_data.shared_otls_dir

    @property
    def project_otls_dir(self):
        # type: () -> str
        """ The project otls directory """
        return self.project_data.project_otls_dir

    @property
    def cache_path(self):
        # type: () -> str
        """ The cache node path """
        cache_path, _ = node_utils.get_current_cache_path(self.source_node)
        return cache_path

    @property
    def node_metadata(self):
        # type: () -> dict
        """ Get the HDA metadata """
        context = self.source_node.type().nameWithCategory()
        category = self.source_node.type().category().name()
        icon_path = self.source_node.type().icon()
        metadata_dict = {
            "context": context,
            "category": category,
            "icon_path": icon_path
        }
        return metadata_dict

    @BaseExporter.add_to_percentage(10)
    def create_hda_asset_version(self):
        """
        Create the hda asset version on ftrack for the library
        """
        self.ftasset.category = "HDA"

        if self.data['library']:
            self.log("Creating library asset version...")
            self.ftasset.project_name = "Library"

            # create the asset if it does exist
            self.ftasset.create_library_ftrack_asset("hda", self.hda_name)
            self.ftasset.asset_build_name = self.hda_name
            self.ftasset.task_name = self.LIB_TASK

            # get the version publish directory
            major_version = hou.applicationVersion()[0]
            publish_directory = f"{self.shared_otls_dir}/{major_version}"

        else:
            self.log("Creating project asset version...")
            self.ftasset.asset_build_type_name = self.data['asset_build_type_name']
            self.ftasset.asset_build_name = self.data['asset_build_name']
            self.ftasset.task_name = self.data['task_name']
            publish_directory = self.project_otls_dir

        # set the node metadata
        next_version_num = self.ftasset.latest_version_num + 1

        # get publish path
        task_name = self.data['task_name']
        version_padded = str(next_version_num).zfill(3)
        hda_name = f"{self.hda_name}_{task_name}_{version_padded}.hda"
        self.hda_dest_path = os.path.join(publish_directory, hda_name)

        # set publish asset data
        self.data["ext"] = "hda"
        self.data["version_num"] = next_version_num
        self.data["pub_file_path"] = self.hda_dest_path
        self.data["metadata"] = self.node_metadata

        # publish the asset
        self.asset_version = self.ftasset.set_ftrack_data(self.data)
        self.hda_asset_version_id = self.asset_version["id"]
        self.log(f"Asset Version: {self.hda_asset_version_id}")
        self.save_hda_name = self.hda_name

        # if there is a cache path add it in
        if self.cache_path:
            self.ftver.asset_version_id = self.hda_asset_version_id
            self.ftver.add_component("CachePath", self.cache_path)

    @BaseExporter.add_to_percentage(10)
    def create_digital_asset(self):
        """
        Create the digital asset from the data
        """
        self.log("Creating Houdini Digital Asset...")
        version = str(self.data["version_num"])
        self.log(f"Save path: {self.hda_dest_path}")

        # if it's already a digital asset set the version and save
        if hou_utils.is_node_hda(self.source_node):
            self.log("Node is already an HDA")
            definition = self.source_node.type().definition()
            definition.setVersion(version)
            definition.save(self.hda_dest_path)
            self.log(f"Saved: {self.hda_dest_path}")
        else:
            comment = self.data['comment']
            self.log(f"Creating HDA {self.hda_dest_path}")
            self.source_node.createDigitalAsset(
                self.save_hda_name,
                self.hda_dest_path,
                self.save_hda_name,
                comment=comment,
                version=version,
                ignore_external_references=True
            )
        self.log("Created digital asset")


if __name__ == "__main__":
    exporter = HDAExporter()
    exporter.batch_process(sys.argv[1])
