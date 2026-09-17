""" Manage a published shot asset node in houdini """
import os
import hou
from typing import Optional, Any
import ccftrack.asset_version as asset_version
import ccftrack.shot as shot
import ccftrack.query as query
import cccore.utils.cc_logging as cc_logging
import cchoudini.hou_constants as hou_constants
import cchoudini.utils.hou_utils as hou_utils


USE_CACHE_PARM_NAME = hou_constants.USE_CACHE_PARM_NAME


class FTrackHouNode(object):
    """ Functions to manage and switch a node """
    FUNCTION_CMD_FNT = "import cchoudini.node.ftrack_hou_node as fhn;" \
                       "fhn.FTrackHouNode(hou.pwd()).{function_name}()"

    def __init__(self, node, ftver_inst=None, component_name=None, session=None):
        # type: (hou.Node, Optional[asset_version.FtAssetVersion], Optional[str], Optional[Any]) -> None
        """
        Args:
            node: The node to manage
        """
        self.logger = cc_logging.cc_logger()
        self.node = node
        self.reload_parm = None
        self.string_parms = list()
        self.parm_templates = list()
        self.controls_templates = list()

        self.shot_version_ftrack_id = str()
        self.shot_task_ftrack_id = str()
        self.shot_cache_name = str()
        self.shot_cache_path = str()
        self.shot_version_padded = str()

        self._session = None
        self._ftquery = None
        self._ftshot = None
        self._ftver = None

        if ftver_inst:
            self.component_name = component_name
            self.asset_cache_path = ftver_inst.cache_path or str()
            self.version_padded = ftver_inst.version_padded
            self.asset_build_type_name = ftver_inst.asset_build_type_name
            self.asset_build_name = ftver_inst.asset_build_name
            self.asset_version_id = ftver_inst.asset_version_id
            self.asset_task_id = ftver_inst.task_id
            self.session = ftver_inst.session
        else:
            self.component_name = str()
            self.asset_cache_path = str()
            self.version_padded = str()
            self.asset_build_type_name = str()
            self.asset_build_name = str()
            self.asset_version_id = str()
            self.asset_task_id = str()
            self.session = session

    @property
    def session(self):
        # type: () -> Any
        """ Current ftrack session """
        if not self._session:
            self._ftquery = query.FtQuery()
            self._session = self._ftquery.session
        return self._session

    @session.setter
    def session(self, session):
        # type: (Any) -> None
        """ Set the ftrack session """
        self._session = session

    @property
    def ftquery(self):
        # type: () -> query.FtQuery
        """ Ftrack query class instance """
        if not self._ftquery:
            self._ftquery = query.FtQuery(session=self.session)
        return self._ftquery

    @property
    def ftver(self):
        # type: () -> asset_version.FtAssetVersion
        """ Ftrack asset version class instance """
        if not self._ftver:
            self._ftver = asset_version.FtAssetVersion(session=self.session)
        return self._ftver

    @property
    def ftshot(self):
        # type: () -> shot.FtShot
        """ Ftrack shot class instance """
        if not self._ftshot:
            self._ftshot = shot.FtShot(session=self.session)
        return self._ftshot

    @property
    def node_type(self):
        # type: () -> bool
        """ is the main node cache """
        return self.node.type().name()

    @property
    def build_name(self):
        # type: () -> bool
        """ is the main node cache """
        return self.node.parm("build_name").evalAsString()

    def add_ftrack_parameters(self):
        """
        Add the ftrack information to the node
        """
        self.create_switch_parameter()
        self.create_update_button()
        self.create_undeletable_toggle()
        self.create_cache_path_parm()
        self.create_string_parameters()
        self.create_separator()

        # add the parameters to the ftrack folder
        self.add_parameters_to_folder()
        self.add_parameters_to_options_folder()

        # connect to the source file path
        self.connect_node_expressions()
        self.lock_parameters_and_set_expressions()
        self.switch_cache_version()

    def set_parameter(self, parm_name, parm_value):
        # type: (str, str) -> None
        """
        Unlock and set a parameter of a certain name

        Args:
            parm_name: Name of the parameter
            parm_value: Value of the parameter
        """
        self.node.parm(parm_name).lock(0)
        self.node.parm(parm_name).set(parm_value)
        self.node.parm(parm_name).lock(1)

    def add_string_parameter(self, parm_name, parm_value, is_hidden=False):
        # type: (str, str, Optional[bool]) -> None
        """
        Create and add a string parameter to the node

        Args:
            parm_name: Name of the parameter
            parm_value: Value of the parameter
            is_hidden: Hide the parameter
        """
        parm_label_list = parm_name.split("_")
        parm_label_title_list = [word.title() for word in parm_label_list]
        parm_label_title_str = " ".join(parm_label_title_list)
        new_parm = hou.StringParmTemplate(
            parm_name,
            parm_label_title_str,
            1,
            is_hidden=is_hidden,
            default_value=(parm_value,)
        )
        self.string_parms.append(parm_name)
        self.parm_templates.append(new_parm)

    def create_string_parameters(self):
        """
        Build all string parameters
        """
        # add the ftrack display parameters
        self.add_string_parameter("build_type", self.asset_build_type_name)
        self.add_string_parameter("build_name", self.asset_build_name)
        self.add_string_parameter("component_name", self.component_name)
        self.add_string_parameter("asset_version", self.version_padded)

        self.add_string_parameter("asset_task_ftrack_id", self.asset_task_id, is_hidden=True)
        self.add_string_parameter("asset_version_ftrack_id", self.asset_version_id, is_hidden=True)
        self.add_string_parameter("asset_file_name", os.path.basename(self.asset_cache_path))
        self.add_string_parameter("asset_cache_path", self.asset_cache_path, is_hidden=True)

        # add ftrack shot attribute
        self.add_string_parameter("episode", "-")
        self.add_string_parameter("sequence", "-")
        self.add_string_parameter("shot", "-")

        self.add_string_parameter("shot_cache_name",  self.shot_cache_name)
        self.add_string_parameter("shot_version", self.shot_version_padded)

        self.add_string_parameter("shot_task_ftrack_id", self.shot_task_ftrack_id, is_hidden=True)
        self.add_string_parameter("shot_version_ftrack_id", self.shot_version_ftrack_id, is_hidden=True)
        self.add_string_parameter("shot_cache_path", self.shot_cache_path, is_hidden=True)

    def create_update_button(self):
        """
        Create the update version button
        """
        update_to_latest_cmd = self.FUNCTION_CMD_FNT.format(function_name="update_node_versions")
        button_template = hou.ButtonParmTemplate(
            "update_to_latest",
            "Update To Latest",
            join_with_next=True,
            script_callback=update_to_latest_cmd,
            script_callback_language=hou.scriptLanguage.Python
        )
        self.controls_templates.append(button_template)

    def create_undeletable_toggle(self):
        """
        Create un deletable toggle parameter
        """
        toggle_template = hou.ToggleParmTemplate(
            name="non_deletable",
            label="Make Non-Deletable"
        )
        self.controls_templates.append(toggle_template)

    def add_parameters_to_folder(self):
        """
        Add the parameters to the ftrack folder
        """
        template_grp = self.node.parmTemplateGroup()
        folder = hou.FolderParmTemplate(
            "ftrack",
            "FTrack",
            folder_type=hou.folderType.Collapsible,
            parm_templates=self.parm_templates
        )
        # add to the template
        template_grp.insertBefore((0,), folder)
        self.node.setParmTemplateGroup(template_grp)

    def add_parameters_to_options_folder(self):
        """
        Add the parameters to the ftrack folder
        """
        template_grp = self.node.parmTemplateGroup()
        folder = hou.FolderParmTemplate(
            "options",
            "Options",
            folder_type=hou.folderType.Simple,
            parm_templates=self.controls_templates
        )
        # add to the template
        template_grp.insertBefore((0,), folder)
        self.node.setParmTemplateGroup(template_grp)

    def create_separator(self):
        """
        Add a separator to the ftrack group
        """
        separator_template = hou.SeparatorParmTemplate("end_group")
        self.parm_templates.append(separator_template)

    def create_switch_parameter(self):
        """
        Create the lock version parameter
        """
        default_value = 0 if self.asset_version_id else 1
        switch_cmd = self.FUNCTION_CMD_FNT.format(function_name="switch_cache_version")
        lock_version_template = hou.MenuParmTemplate(
            "switch_cache",
            "Switch cache",
            menu_items=tuple(["/cc/pipeline/nodes/icons/asset.png",
                              "/cc/pipeline/nodes/icons/shot.png"]),
            menu_labels=tuple(["asset", "shot"]),
            is_button_strip=True,
            strip_uses_icons=True,
            join_with_next=True,
            default_value=default_value,
            script_callback=switch_cmd,
            script_callback_language=hou.scriptLanguage.Python,
        )
        self.controls_templates.append(lock_version_template)

    def switch_cache_version(self):
        """
        Switch the path of the cache node based on the buttons
        """
        value = self.node.parm("switch_cache").eval()
        parm_list = ["asset_cache_path", "shot_cache_path"]
        cache_path = self.node.parm(parm_list[value]).eval()
        self.set_parameter(USE_CACHE_PARM_NAME, cache_path)
        self.set_parameter("use_cache_name", os.path.basename(cache_path))

    def create_cache_path_parm(self):
        """
        Create the cache being used parameters
        """
        use_cache_path_parm = hou.StringParmTemplate(
            USE_CACHE_PARM_NAME,
            "Use Cache Path",
            1,
        )
        self.controls_templates.append(use_cache_path_parm)
        use_cache_name_parm = hou.StringParmTemplate(
            "use_cache_name",
            "Use Cache Name",
            1,
        )
        self.controls_templates.append(use_cache_name_parm)

    def lock_parameters_and_set_expressions(self):
        """
        Lock the string parameters and set the shot expressions
        """
        # lock the parameters created and reset
        for parm_name in self.string_parms:
            self.node.parm(parm_name).lock(1)

        # set the shot expressions
        parm_expression_dict = {"episode": "$EP", "sequence": "$SEQ", "shot": "$SHOT"}
        for parm_name, expression in parm_expression_dict.items():
            self.create_expression(parm_name, expression, self.node)

    @staticmethod
    def create_expression(parm_name, expression, node):
        # type: (str, str, hou.Node) -> None
        """
        Create an expression on a node

        Args:
            parm_name: Name of the parameter to set
            expression: The expression to set
            node: Node to set it on
        """
        file_parameter = node.parm(parm_name)
        file_parameter.lock(0)

        node.allowEditingOfContents()
        if file_parameter.keyframes():
            file_parameter.deleteAllKeyframes()

        file_parameter.setExpression(
            expression,
            language=hou.exprLanguage.Hscript,
            replace_expression=True
        )
        file_parameter.lock(1)

    def connect_node_expressions(self):
        """
        Connect the file paths to be sourced at one location
        """
        loading_node = None
        if self.node_type == "geo":
            loading_node = hou_utils.find_all_subnodes_of_types(self.node, ["alembic"])[0]
            self.reload_parm = loading_node.parm("reload")

        elif self.node_type == "alembicarchive":
            self.reload_parm = self.node.parm("buildHierarchy")
            loading_node = hou_utils.find_all_subnodes_of_types(self.node, ["alembicxform"])[0]
            self.create_expression("fileName", f'chs("{USE_CACHE_PARM_NAME}")', self.node)

        if loading_node:
            self.create_expression("fileName", f'chs("../{USE_CACHE_PARM_NAME}")', loading_node)

    def set_shot_data(self, shot_data):
        # type: (dict) -> None
        """
        Set the shot data parameters

        Args:
            shot_data: Dictionary of shot information
        """
        for parm_name, value in shot_data.items():
            self.set_parameter(parm_name, value)
        self.node.parm("switch_cache").set(1)
        self.switch_cache_version()
