""" Asset publisher in maya """
import os
import sys
import shutil
import tempfile
import maya.cmds as cmds
from ccgeneral.wizard.exporter.base_exporter import BaseExporter


# initialize maya standalone
try:
    import maya.standalone
    maya.standalone.initialize()
except (TypeError, RuntimeError):
    pass


class CleanupAssetExporter(BaseExporter):
    def __init__(self):
        super().__init__()

    def export(self):
        """
        Export the asset and publish it to FTrack
        """
        self.log(f"Asset publish complete: {self.data}")
        if not cmds.pluginInfo("fbxmaya", query=True, loaded=True):
            cmds.loadPlugin("fbxmaya")

        fbx_file_path = self.data["fbx_file_path"]
        cmds.file(fbx_file_path, i=True)
        import time
        self.log(f"Asset publish co")
        time.sleep(2)


if __name__ == "__main__":
    exporter = CleanupAssetExporter()
    exporter.batch_process(sys.argv[1])
