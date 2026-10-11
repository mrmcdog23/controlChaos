""" Context for Unreal to get the paths for assets and shots """
import os
import unreal as ue
import cccore.file_env.context as context
import cccore.utils.file_utils as file_utils
import ccunreal.unreal_constants as unreal_constants
from typing import Optional

# constants
MATERIAL = unreal_constants.MATERIAL
LS_PREFIX = unreal_constants.LS_PREFIX
MP_PREFIX = unreal_constants.MP_PREFIX


class UnrealContext(context.Context):
    ue_shots_dir = "/Game/Shots"
    ue_assets_dir = "/Game/Build"

    @property
    def ue_sequence_directory(self):
        """ Path to an unreal shot path """
        if self.is_build:
            return str()
        if self.episode:
            sequence_directory = file_utils.join_from_list(self.ue_shots_dir, self.episode, self.sequence)
        else:
            sequence_directory = file_utils.join_from_list(self.ue_shots_dir, self.sequence)
        return sequence_directory

    @property
    def ue_shot_directory(self):
        """ Path to an unreal shot path """
        if self.is_build:
            return str()
        return file_utils.join_from_list(self.ue_sequence_directory, self.shot)

    @property
    def ue_shot_version_directory(self):
        # type: () -> str
        """ Path to an unreal shot path """
        return file_utils.join_from_list(self.ue_shot_directory, self.version_padded)

    @property
    def ue_asset_directory(self):
        # type: () -> str
        """ Path to an unreal shot path """
        asset_directory = file_utils.join_from_list(self.ue_assets_dir, self.asset_build, self.task)
        return asset_directory

    @property
    def ue_asset_version_directory(self):
        # type: () -> str
        """ Path to an unreal asset path """
        asset_version_directory = file_utils.join_from_list(self.ue_asset_directory, self.version_padded)
        return asset_version_directory

    @property
    def ue_material_version_directory(self):
        # type: () -> str
        """ Path to an unreal asset path material directory """
        material_version_directory = file_utils.join_from_list(self.ue_asset_version_directory, MATERIAL)
        return material_version_directory

    @property
    def ue_skeleton_mesh_path(self):
        # type: () -> str
        """ Path to an unreal skeleton asset path """
        skeleton_name = f"{self.asset_build}_{self.task}_PUB_{self.version}"
        ue_skeleton_path = file_utils.join_from_list(self.ue_asset_version_directory, skeleton_name)
        return ue_skeleton_path

    @property
    def disk_project_root(self):
        # type: () -> str
        """ The root folder of the project """
        return os.path.dirname(os.environ["UE_PROJECT_PATH"])

    @property
    def disk_shots_dir(self):
        # type: () -> str
        """ The shots directory of the project on disk """
        return file_utils.join_from_list(self.disk_project_root, "Content", "Shots")

    @property
    def disk_shot_dir(self):
        # type: () -> str
        """ The shot directory on disk """
        return file_utils.join_from_list(self.disk_shots_dir, self.episode, self.sequence, self.shot)

    @property
    def versions(self):
        # type: () -> list[str]
        """
        List all the version folders in the asset directory
        """
        version_folders = ue.EditorAssetLibrary.list_assets(
            self.ue_asset_directory, recursive=False, include_folder=True)
        versions = [ue.Paths.get_base_filename(ver[:-1]) for ver in version_folders]
        versions.reverse()
        return versions

    @property
    def latest_version(self):
        # type: () -> Optional[str]
        """ The latest imported asset version """
        if self.versions:
            return self.versions[0]

    @property
    def project_map_name(self):
        # type: () -> str
        """ Name of the shot map """
        return f"{MP_PREFIX}_{self.project_name}_world"

    @property
    def project_map_path(self):
        # type: () -> str
        """ Path to the shot map """
        return f"{self.ue_shots_dir}/{self.project_map_name}"

    @property
    def ls_master_name(self):
        # type: () -> str
        """ Name of the master level sequence """
        return f"{LS_PREFIX}_{self.full_sequence_name}_master_sequence"

    @property
    def ls_master_path(self):
        # type: () -> str
        """ Path to the master level sequence """
        return f"{self.ue_sequence_directory}/{self.ls_master_name}"

    @property
    def ls_name(self):
        # type: () -> str
        """ Name of the shot level sequence """
        return f"{LS_PREFIX}_{self.full_shot_name}"

    @property
    def ls_path(self):
        # type: () -> str
        """ Path to the shot level sequence """
        return f"{self.ue_shot_directory}/{self.ls_name}"

    @property
    def map_name(self):
        # type: () -> str
        """ Name of the shot level sequence """
        return f"{MP_PREFIX}_{self.full_shot_name}"

    @property
    def map_path(self):
        # type: () -> str
        """ Path to the shot level sequence """
        return f"{self.ue_shot_directory}/{self.map_name}"

    @property
    def shot_plates_dir(self):
        # type: () -> str
        """ Path to the media source """
        return f"{self.ue_shot_directory}/Plates"

    @property
    def ls_turntable_path(self):
        # type: () -> str
        """ Path to the level sequence turntable """
        ls_turntable = f"{self.ue_asset_directory}/{self.version_padded}" \
                       f"/Turntable/{LS_PREFIX}_{self.asset_build}_{self.version_padded}"
        return ls_turntable

    @property
    def map_turntable_path(self):
        # type: () -> str
        """ Path to the level sequence turntable """
        ls_turntable = f"{self.ue_asset_directory}/{self.version_padded}" \
                       f"/Turntable/{MP_PREFIX}_{self.asset_build}_{self.version_padded}"
        return ls_turntable
