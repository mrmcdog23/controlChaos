""" Manage an HDA and its properties """
import hou
import os
from typing import Any, Optional
import cchoudini.utils.hou_utils as hou_utils
import cccore.utils.cc_logging as cc_logging


class HDA(object):
    """
    Make a node an HDA property
    """
    def __init__(self, node=None):
        # type: (Optional[hou.Node]) -> None
        """
        Args:
            node: Node to check hda properties
        """
        self.node = node
        self.logger = cc_logging.cc_logger()

    @property
    def name(self):
        # type: () -> str
        """
        Name of the hda
        """
        return self.node.type().name()

    @property
    def definition(self):
        # type: () -> str
        """
        Path of the hda definition
        """
        return self.node.type().definition()

    @property
    def is_digital_asset(self):
        # type: () -> bool
        """
        Is the node a digital asset
        """
        return self.definition is not None

    @property
    def is_saved_local(self):
        # type: () -> bool
        """
        Property if the definition saved locally
        """
        return self.definition_is_local(self.definition)

    @staticmethod
    def definition_is_local(definition):
        # type: (Any) -> bool
        """
        Is the definition local or published

        Args:
            definition: The hda definition

        Returns:
            True if the hda is local
        """
        if hou.homeHoudiniDirectory() in definition.libraryFilePath():
            return True
        return False

    @property
    def is_published_digital_asset(self):
        # type: () -> bool
        """
        Is it a digital asset saved locally
        """
        return self.is_digital_asset and not self.is_saved_local

    def make_local(self):
        """
        Make the hda local
        """
        if not self.is_digital_asset:
            return
        if self.is_saved_local:
            return

        node_type = self.node.type().name()
        local_file_path = os.path.join(
            hou.homeHoudiniDirectory(),
            "otls",
            node_type + ".hda"
        )

        self.logger.info("Copying HDA definition locally..")
        self.definition.copyToHDAFile(
            local_file_path,
            new_name=node_type
        )

        self.logger.info("Installing new HDA to Asset Library.")
        hou.hda.installFile(local_file_path, force_use_assets=True)
        os.chmod(local_file_path, 0o777)

        if hou.isUIAvailable():
            hou_utils.hou_messagebox(
                "Houdini Digital Asset",
                f"HDA was saved to:\n{local_file_path}",
                "info"
            )

    @staticmethod
    def get_node_definitions_dict():
        # type: () -> dict
        """
        Get a dictionary of node type names
        to the list of definition files
        """
        node_definitions_dict = dict()
        for definition_file in hou.hda.loadedFiles():
            definition = hou.hda.definitionsInFile(definition_file)[0]
            node_type = definition.nodeTypeName()
            definition_files = node_definitions_dict.get(node_type, list())
            definition_files.append(definition_file)
            node_definitions_dict[node_type] = definition_files
        return node_definitions_dict

    @property
    def definition_files(self):
        # type: () -> list[str]
        """ Get a list of the nodes file path definitions """
        node_definitions_dict = self.get_node_definitions_dict()
        return node_definitions_dict[self.name]

    def remove_local_definitions(self):
        """
        Remove all files that are not published
        """
        for definition_file in self.definition_files:
            definition = hou.hda.definitionsInFile(definition_file)[0]
            if self.definition_is_local(definition):
                hou.hda.uninstallFile(definition_file)

    @property
    def published_definition_files(self):
        # type: () -> list[str]
        """
        Get a list of the nodes definition files

        Returns:
            published_definitions: List of published hda paths
        """
        published_definitions = list()
        for definition_file in self.definition_files:
            definition = hou.hda.definitionsInFile(definition_file)[0]
            if not self.definition_is_local(definition):
                published_definitions.append(definition_file)
        published_definitions.sort()
        return published_definitions

    def set_to_latest(self):
        """
        Set the hda definition to the latest version path
        """
        latest_definition_path = self.published_definition_files[-1]
        hou.hda.installFile(latest_definition_path, force_use_assets=True)
