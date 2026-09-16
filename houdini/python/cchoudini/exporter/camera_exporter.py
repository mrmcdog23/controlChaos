""" Export and publish a camera out of houdini """
import os
import sys
import hou
import cccore.file_env.context as context
import cccore.utils.file_utils as file_utils
import cccore.data.server_data as server_data
import ccgeneral.exporter.base_exporter as base_exporter
import ccftrack.publish as publish
import ccftrack.query as query


class CameraExporter(base_exporter.BaseExporter):
    """
    Exporter to create and publish a Houdini Digital Asset
    """
    def __init__(self):
        super(CameraExporter, self).__init__()
        self.next_version_num = None
        self.project_data = server_data.ProjectData()

    @staticmethod
    def get_camera_name_to_path():
        # type: () -> dict
        """
        Get a dictionary of the camera name to its path

        Returns:
            camera_name_to_path_dict: Camera name to its node
        """
        camera_name_to_path_dict = dict()
        for node in hou.node("/obj/").allSubChildren():
            if node.type().name() != "cam":
                continue
            camera_name_to_path_dict[node.name()] = node
        return camera_name_to_path_dict

    def export_otls_camera(self, node, otls_path):
        """
        Export the otls camera
        """
        context_node = node.parent()
        file_utils.create_directories(os.path.dirname(otls_path))
        self.log(f"cpio exporting {otls_path}")
        context_node.saveChildrenToFile([node], [], otls_path)
        return otls_path

    def create_alembic_camera(self, abc_path, hou_camera_path):
        # type: (str, str) -> None
        """
        Create the alembic node to export
        the camera as an alembic cache

        Args:
            abc_path: Path of the alembic file
            hou_camera_path: Path of the camera to cache
        """
        alembic_camera_node = hou.node("/out").createNode("alembic", "camera_export")
        alembic_camera_node.parm("trange").set(1)
        alembic_camera_node.parm("initsim").set(1)
        alembic_camera_node.parm("filename").set(abc_path)
        alembic_camera_node.parm("root").set("/obj/")
        alembic_camera_node.parm("objects").set(hou_camera_path)
        alembic_camera_node.parm("execute").pressButton()
        alembic_camera_node.destroy()
        self.log(f"Exporting camera as an alembic....{abc_path}")

    def create_fbx_camera(self, fbx_path, hou_camera_path):
        # type: (str, str) -> None
        """
        Create the filmbox node to export the camera as fbx cache

        Args:
            fbx_path: Path of the alembic file
            hou_camera_path: Path of the camera to cache
        """
        fbx_camera_node = hou.node("/out").createNode("filmboxfbx", "tmp_fbx_export")
        fbx_camera_node.parm("trange").set(1)
        fbx_camera_node.parm("startnode").set(hou_camera_path)
        fbx_camera_node.parm("sopoutput").set(fbx_path)
        fbx_camera_node.parm("execute").pressButton()
        fbx_camera_node.destroy()
        self.log(f"Exporting camera as an fbx....{fbx_path}")

    def export(self):
        """
        Export the asset and publish it to ftrack
        """
        # create symlink
        self.add_progress(10)

        # write the data out
        self.log("Publishing alembic cameras..")
        camera_name_to_path_dict = self.get_camera_name_to_path()
        chunk_size = 60 / len(camera_name_to_path_dict)

        additional_components_dict = dict()
        camera_name_to_path_dict = self.get_camera_name_to_path()
        for camera_name in self.data["namespaces"]:
            self.add_progress(int(chunk_size))
            node = camera_name_to_path_dict[camera_name]
            self.log(f"Publishing alembic {camera_name}..")

            node_path = node.path()
            hou_camera_path = node_path.replace("/obj/", "")

            # use the node name for the aov
            self.data["aov"] = node.name()

            # get the export alembic path
            ctx = context.Context(overrides=self.data)
            ctx.use_ext = "abc"
            ctx.use_subfolder = "abc"

            # get the next version on ftrack or on disk
            if not self.next_version_num:
                self.next_version_num = query.FtQuery().get_correct_version(ctx.hou_sequence_path)
                self.data["version_num"] = self.next_version_num

            # get the next file path
            ctx.use_version = self.next_version_num

            # export the alembic camera
            abc_path = ctx.abc_sequence_path
            self.create_alembic_camera(abc_path, hou_camera_path)
            additional_components_dict[f"{camera_name}_ABC"] = abc_path

            # create the alembic path
            fbx_path = ctx.fbx_sequence_path
            node_path = node.parent().parent().path()
            self.create_fbx_camera(fbx_path, node_path)
            additional_components_dict[f"{camera_name}_FBX"] = fbx_path

            # export otls camera
            otls_path = ctx.otls_sequence_path
            self.export_otls_camera(node, otls_path)
            additional_components_dict[f"{camera_name}_OTLS"] = otls_path

        self.add_progress(80)
        self.data["additional_components"] = additional_components_dict
        publish_inst = publish.FtrackPublish(self.data)
        self.asset_version = publish_inst.asset_version
        asset_version_id = self.asset_version["id"]
        self.log(f"Asset Version: {asset_version_id}")
        self.finish_exporter_process()


if __name__ == "__main__":
    exporter = CameraExporter()
    exporter.batch_process(sys.argv[1])
