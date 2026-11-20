""" The unreal shot creator """
import os
import sys
import ccunreal.utils.unreal_utils as unreal_utils
import ccunreal.utils.project_folders as project_folders

# add the standalone path to the sys paths
pipeline_root = os.environ["PIPELINE_ROOT"]
sys.path.append(f"{pipeline_root}/standalone/python/creators")
from shot_creator import ShotCreator
from asset_creator import AssetCreator


class UEShotCreator(ShotCreator):
    def __init__(self, parent):
        super().__init__(parent=parent)

    def create_context(self):
        """
        Create the sequence and shots
        """
        super().create_context()

        # create the folders in unreal
        project_folders.create_project_folders()


class UEAssetCreator(AssetCreator):
    def __init__(self, parent):
        super().__init__(parent=parent)

    def create_asset(self):
        """
        Create the sequence and shots
        """
        super().create_asset()

        # create the folders in unreal
        project_folders.create_project_folders()


def launch_shot_creator():
    """ Launch the shot creator """
    unreal_utils.launch_unreal_win(UEShotCreator)


def launch_asset_creator():
    """ Launch the asset creator """
    unreal_utils.launch_unreal_win(UEAssetCreator)
