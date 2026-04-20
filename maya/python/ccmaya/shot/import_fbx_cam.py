""" Export FBX cameras to Unreal """
import unreal as ue
import cccore.utils.file_utils as file_utils
import ccunreal.utils.api_wrap as api_wrap
import ccunreal.utils.unreal_utils as unreal_utils


class ImportFBXCam(object):
    title = "Import Unreal Cameras"

    def __init__(self, import_dir):
        fbx_files = file_utils.get_files_recursively(import_dir, ["fbx"])
        for fbx_path in fbx_files:
            self.import_camera_animation(fbx_path)

    def import_camera_animation(self, fbx_path):
        # type: (str) -> None
        """
        Import a camera into the level sequence by
        creating then importing the fbx afterward

        Args:
            fbx_path: Path of the camera fbx file
        """
        # check for existing camera first
        camera_name = f"{self.ftver.full_shot_name}_cam"

        # spawn a no8 camera to the map
        camera_actor = ue.EditorLevelLibrary.spawn_actor_from_class(
            ue.CineCameraActor, ue.Vector(0, 0, 0))

        # add to the level sequence
        api_wrap.add_actors_to_current_sequence([camera_actor])
        binding = unreal_utils.find_binding_by_actor_class(ue.CineCameraActor, self.ls)

        # set tag and label
        camera_actor.tags = [fbx_path]
        camera_actor.set_actor_label(camera_name)

        # apply the sequence animation
        ue.CameraFbxImporter.load_camera(
            self.map_master, self.ls, [binding],
            unreal_utils.camera_ue_options(),
            fbx_path,
        )


def import_cams(import_dir):
    ImportFBXCam(import_dir)