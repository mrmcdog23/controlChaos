""" base class for shot assets in applications """
import ftrack_api
from typing import Optional, Any
import ccftrack.query as query
import ccftrack.asset_version as ft_asset_version
import cccore.utils.cc_logging as cc_logging
import cccore.utils.context_utils as context_utils


class BaseShotAsset(object):
    """
    From a namespace of ftrack attribute get
    all the data related to the asset
    """
    def __init__(self, node, session=None):
        # type: (Any, Optional[ftrack_api.session]) -> None
        """
        Args:
            node: The houdini node
            session: Ftrack connection
        """
        self._component = None
        self._current_path = None
        self._number_to_asset_version = None
        self._current_version_num = None
        self._latest_version_num = None

        self.node = node
        self.logger = cc_logging.cc_logger()
        self.ftquery = query.FtQuery(session=session)
        self.ftver = ft_asset_version.FtAssetVersion(session=self.ftquery.session)
        self.set_asset_version()

    def clear(self):
        """
        Reset all data
        """
        self._component = None
        self._current_path = None
        self._number_to_asset_version = None
        self._current_version_num = None
        self._latest_version_num = None

    @property
    def current_version_num(self):
        # type: () -> int
        """ Get the current version number """
        if not self._current_version_num:
            self._current_version_num = self.ftver.latest_version_num
        return self._current_version_num

    @property
    def latest_version_num(self):
        # type: () -> int
        """ Get the latest version number """
        if not self._latest_version_num:
            self._latest_version_num = self.ftver.latest_version_num
        return self._latest_version_num

    @property
    def node_type(self):
        # type: () -> str
        """ Node type name """
        raise NotImplemented

    @property
    def node_path(self):
        # type: () -> str
        """ Path of the node """
        raise NotImplemented

    @property
    def source_path(self):
        # type: () -> str
        """ Path of the node """
        raise NotImplemented

    def select(self):
        """ Select the node """
        raise NotImplemented

    def toggle(self):
        """ Toggle the node visibility """
        raise NotImplemented

    def update_node(self, new_path):
        # type: (str) -> None
        """
        Update the node to the new path

        Args:
            new_path: Path to update to
        """
        raise NotImplemented

    @property
    def ftrack_id(self):
        # type: () -> str
        """
        The ftrack id
        """
        return self.ftver.asset_version_id

    @property
    def asset_version(self):
        # type: () -> ftrack_api.entity.asset_version
        """
        The objects current asset version
        """
        return self.ftver.asset_version

    def set_asset_version(self):
        """
        Set the asset version from the component
        """
        if not self.is_valid_asset:
            return
        asset_version_id = self.component["version"]["id"]
        self.ftver.asset_version_id = asset_version_id

    @property
    def current_version_int(self):
        # type: () -> int
        """ The current version number as an integer """
        ctx = context_utils.get_context_from_path(self.current_path)
        return ctx.version_int

    @property
    def component(self):
        # type: () -> ftrack_api.entity.component
        """
        Get the ftrack component for the path

        Returns:
            _component: The component found on ftrack
        """
        if self._component:
            return self._component
        self._component = self.ftquery.component_from_path(self.current_path)
        return self._component

    @property
    def component_name(self):
        # type: () -> Optional[str]
        """ Name of the component """
        if self.component:
            return self.component["name"]

    @property
    def is_valid_asset(self):
        # type: () -> bool
        """ Check the asset is valid and matches the naming convention """
        if not self.current_path:
            return False
        try:
            ctx = context_utils.get_context_from_path(self.current_path)
        except (KeyError, AttributeError):
            return False
        if not ctx:
            return False
        if not self.component:
            return False
        return True

    @property
    def number_to_asset_version(self):
        # type: () -> dict
        """
        Get a dictionary of the component
        to the asset version and number

        Returns:
            _number_to_asset_version: Number to version
        """
        if not self._number_to_asset_version:
            self._number_to_asset_version = self.ftver.component_versions(self.component_name)
        return self._number_to_asset_version

    def update_to_version(self, current_version):
        # type: (str) -> None
        """
        Update the asset version to the new version

        Args:
            current_version: New version to set to
        """
        asset_version = self.number_to_asset_version[int(current_version)]
        self.ftver.asset_version_id = asset_version["id"]

        component_path_dict = self.ftver.get_component_path_dict()
        new_path = component_path_dict[self.component_name]
        self.logger.info(f"Path: {new_path}")
        self.update_node(new_path)
