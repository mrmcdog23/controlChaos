""" No8Cache node management and functions """
import os
import shutil
import hou
from typing import Optional
import cccore.utils.cc_logging as cc_logging
import cccore.file_env.context as context
import cccore.utils.file_utils as file_utils
import cccore.utils.sequence_utils as sequence_utils
import ccftrack.shot as shot
import ccftrack.asset as asset
import ccftrack.query as query
import cchoudini.utils.hou_utils as hou_utils


# class constants
BUILD_DEFAULT_TASK_LIST = ["lookdev", "modeling", "rigging", "texture"]
SHOT_DEFAULT_TASK_LIST = ["animation", "layout", "lighting", "fx"]
EXTENSION_TYPES = {"bgeo": "bgeo.sc"}
PY_COMMAND = "from cchoudini.node.cccache import No8CacheNode;No8CacheNode(hou.pwd())"


class No8CacheNode(object):
    """
    Class for management of cccache node
    """
    def __init__(self, cc_cache_node):
        # type: (hou.Node) -> None
        """
        Args:
            cc_cache_node: Node to manage
        """
        self.version = int()
        self.output_path = str()
        self.logger = cc_logging.cc_logger()
        self.cc_cache_node = cc_cache_node

    def get_cache_type(self):
        # type: () -> str
        """
        Get the cache type label

        Returns:
            cache_type: The cache type to create
        """
        parameter = self.cc_cache_node.parm("cache_type")
        labels = list(parameter.menuLabels())
        cache_type = labels[parameter.eval()].split(".")[0]
        return cache_type

    def hide_redundant_parms(self):
        """
        Hide redundant parameters
        """
        # getting the template
        template_grp = self.cc_cache_node.parmTemplateGroup()
        parms_names = ["set_to_latest",
                       "abc_set_to_latest",
                       "abc_create_new_version"
                       ]
        for parms_name in parms_names:
            parm_template = template_grp.find(parms_name)
            if parm_template:
                template_grp.hide(parm_template, True)

        # setting the template
        self.cc_cache_node.setParmTemplateGroup(template_grp)

    def create_task_and_refresh(self):
        """
        Create the task parameter
        """
        # add to the bgeo and vdb tab
        self.create_task_parameters("file_name", "task_name", "refresh")
        # add to the alembic tab
        self.hide_redundant_parms()

    def create_new_version(self):
        """
        Get the next ftrack and disk version and if is
        the current path then skip setting it if not
        then set the expression.
        """
        output_path = self.cc_cache_node.parm("output_path").evalAsString()
        next_version_num = query.FtQuery().get_correct_version(output_path)
        self.cc_cache_node.parm("version").set(next_version_num)

    def create_task_parameters(self, after_parm, menu_parm, refresh_parm):
        # type: (str, str, str) -> None
        """
        Create the task and refresh parameters

        Args:
            after_parm: Name of the parameter to create after
            menu_parm: Name of the task menu parameter
            refresh_parm: Name of the refresh button parameter
        """
        ptg = self.cc_cache_node.parmTemplateGroup()
        index = ptg.findIndices(after_parm)

        # get the task list
        ctx = context.Context()
        if ctx.is_asset:
            default_task_list = BUILD_DEFAULT_TASK_LIST
        else:
            default_task_list = SHOT_DEFAULT_TASK_LIST

        # task create menu
        task_menu = hou.MenuParmTemplate(
            menu_parm,
            "Task Name",
            default_task_list,
            join_with_next=True
        )

        # create button
        refresh_task_list_cmd = f"{PY_COMMAND}.refresh_task_list()"
        button = hou.ButtonParmTemplate(
            refresh_parm, "Refresh",
            script_callback=refresh_task_list_cmd,
            script_callback_language=hou.scriptLanguage.Python
        )

        # add to the template
        ptg.insertBefore(index, button)
        ptg.insertBefore(index, task_menu)

        # add to the template
        self.cc_cache_node.setParmTemplateGroup(ptg)
        if ctx.task:
            hou_utils.set_menu_text(self.cc_cache_node, menu_parm, ctx.task)

    def refresh_task_list(self):
        """
        Refresh the task list by reading ftrack
        """
        # get tasks
        ftshot = shot.FtShot()
        ftasset = asset.FtAsset(session=ftshot.session)
        ctx = context.Context()
        if ctx.is_asset:
            task_names = ftasset.get_asset_task_names(ctx.asset_build)
        else:
            task_names = ftshot.get_shot_task_names(ctx.sequence, ctx.shot)
        hou_utils.update_menu_list(
            self.cc_cache_node, "task_name", task_names)

    def on_create(self):
        """
        When node is created set the colour and add the status parm
        """
        self.cc_cache_node.setColor(hou.Color(0.7, 0.5, 1))

        # lock parameters in list
        parm_list = ["file_name", "output_path"]
        for parm_name in parm_list:
            self.cc_cache_node.parm(parm_name).lock(1)

        # get tasks
        self.create_task_and_refresh()
        self.cc_cache_node.parm("cache_name").set(self.cc_cache_node.name())

    @staticmethod
    def set_parm_expression(node, parm_name, expression):
        # type: (hou.Node, str, str) -> None
        """
        Break and set the expression on the parameter and relock

        Args:
            node: Node to set parameter on
            parm_name: Name of the parameter to set
            expression: New expression to set
        """
        # set the base name of the description
        descriptive_parm = node.parm(parm_name)
        descriptive_parm.lock(0)
        descriptive_parm.deleteAllKeyframes()
        descriptive_parm.setExpression(expression,
                                       language=hou.exprLanguage.Hscript,
                                       )
        descriptive_parm.lock(1)

    @property
    def task_name(self):
        # type: () -> str
        """
        Get the select task name based on the selected cache type
        """
        return self.cc_cache_node.parm("task_name").evalAsString()

    def get_node_specific_data(self):
        # type: () -> dict
        """
        Get the selected nodes frame range. This will contain
        the start frame, end frame and sequence version

        Returns:
            node_specific_data: The selected nodes data
        """
        self.output_path = self.cc_cache_node.parm("output_path").evalAsString()
        cache_type = self.get_cache_type()
        print(cache_type, self.cc_cache_node.path())
        if cache_type == "fbx":
            # get the fbx cache frame range
            start, end = hou_utils.get_frame_range(
                self.cc_cache_node,
                range_parm="trange_fbx",
                start_parm="f_fbx1",
                end_parm="f_fbx2"
            )
            subnode_type = "rop_fbx"

        elif cache_type == "abc":
            # get the alembic cache frame range
            start, end = hou_utils.get_frame_range(
                self.cc_cache_node,
                range_parm="trange2__",
                start_parm="abc_f1",
                end_parm="abc_f2"
            )
            subnode_type = "rop_alembic"

        else:
            # get the geo cache frame range
            start, end = hou_utils.get_frame_range(self.cc_cache_node)
            subnode_type = "filecache::2.0"

        # store new data in a dictionary
        node_specific_data = {"start": start,
                              "end": end,
                              "version_num": self.version,
                              "output_path": self.output_path,
                              "subnode_type": subnode_type,
                              "cache_type": cache_type,
                              "file_sequences": [self.output_path]
                              }
        return node_specific_data

    @staticmethod
    def do_save_changes_check():
        """
        Check for changes before caching
        """
        buttons = ["Save and Cache", "Cancel"]
        response = hou_utils.hou_messagebox(
            "Save file",
            "Hip File has unsaved changes",
            "question",
            buttons=buttons
        )
        return response == "Save and Cache"

    def submit(self):
        """
        Submit the cache either to the farm or run locally
        """
        input_nodes = hou_utils.input_nodes_of_type(self.cc_cache_node)
        if not input_nodes:
            hou_utils.hou_messagebox("No Inputs",
                                     "No input nodes found",
                                     "critical"
                                     )
            return

        create_cache = self.do_save_changes_check()
        if not create_cache:
            return

        local_or_farm = self.cc_cache_node.parm("local_or_farm").eval()
        self.logger.info(f"Submit mode: {local_or_farm}")
        self.submit_cache_local()

    def submit_cache_local(self, start=None, end=None):
        # type: (Optional[int], Optional[int]) -> None
        """
        Generate the selected cache locally

        Args:
            start: First range to cache
            end: End frame to cache
        """
        node_data = self.get_node_specific_data()
        self.output_path = node_data["output_path"]
        self.logger.info(f"Output Path: {self.output_path}")
        output_dir = os.path.dirname(self.output_path)
        file_utils.create_directories(output_dir)

        subnode = hou_utils.find_subnode_of_type(self.cc_cache_node,
                                                 node_data["subnode_type"]
                                                 )

        if start and end:
            # override the frame range if given
            self.logger.info(f"Overriding frame range: {start}-{end}")
            hou_utils.set_rop_frame_range(self.cc_cache_node, start, end)

        self.logger.info(f"Executing cache...{subnode.path()}")
        subnode.parm("execute").pressButton()
        cache_type = node_data["cache_type"]

        if hou.isUIAvailable():
            # write the metadata to a file for deadline
            self.save_metadata()
            hou_utils.hou_messagebox("Generated Cache",
                                     f"Generated cache type {cache_type}",
                                     "info"
                                     )
        else:
            self.logger.info(self.output_path)
            seq_data = sequence_utils.get_sequence_data(self.output_path)
            message = f"Generated: {seq_data.padded_path}"
            if cache_type == "abc":
                self.logger.info(f"Generated: {self.output_path} {seq_data.frame_range}")
            elif start and end:
                self.logger.info(f"{message} {start}-{end}")
            else:
                self.logger.info(f"{message} {seq_data.frame_range}")

    def save_metadata(self, data=None):
        """
        Save the node metadata
        """
        ctx = context.Context()
        data = data or dict()
        data.update(ctx.as_dict())
        wip_file_path = hou.hipFile.name()
        data["wip_file_path"] = wip_file_path
        data["category"] = "Cache"
        data["task_name"] = self.task_name

        # save the node data to the dictionary
        data["node_path"] = self.cc_cache_node.path()

        # update the frame range in the data
        node_data = self.get_node_specific_data()
        data.update(node_data)

        # get the metadata file path
        basename = file_utils.get_file_name(wip_file_path)
        metadata_path = file_utils.temp_file_path(basename, "metadata")
        file_utils.write_json(metadata_path, data)
        self.logger.info(f"Metadata Path: {metadata_path}")

        # create the metadata directory
        wip_metadata_dir = file_utils.get_metadata_dir(self.output_path, create=True)

        # copy the metadata to the cache directory to know how to publish
        wip_metadata_path = os.path.join(wip_metadata_dir, os.path.basename(metadata_path))
        self.logger.info(f"Copying ...{metadata_path} to {wip_metadata_path}")
        shutil.copy(metadata_path, wip_metadata_path)
        return node_data, metadata_path

    @property
    def cc_wedger_node(self):
        # type: () -> Optional[hou.Node]
        """
        Get the wedger node
        """
        for input_node in self.cc_cache_node.inputAncestors():
            is_wedger = "ccwedger" in input_node.type().name()
            if is_wedger:
                return input_node
