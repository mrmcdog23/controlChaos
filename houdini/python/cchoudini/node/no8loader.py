""" Houdini loader of assets """
import os
import hou
import ccftrack.shot as shot
import ccftrack.asset as asset
import ccftrack.asset_version as asset_version
import cchoudini.utils.hou_utils as hou_utils
import cccore.file_env.context as context
import cccore.deadline.submit as submit
import cccore.utils.file_utils as file_utils
import cccore.utils.cc_logging as cc_logging
import cccore.utils.sequence_utils as sequence_utils

# file constants
COMMAND = "import cchoudini.node.ccloader as ln;ln.No8LoaderNode()"
BUILD_LIST = ["build", "build_task", "build_cache_name", "build_version"]
SHOT_LIST = ["sequence", "shot", "shot_task", "shot_cache_name", "shot_version"]


class No8LoaderNode(object):
    """
    Load houdini node
    """
    def __init__(self, node=None):
        self.ptg = None
        self.node = node
        self.menu_list = BUILD_LIST + SHOT_LIST
        self.logger = cc_logging.cc_logger()
        self.ctx = context.Context()
        self.ftasset = asset.FtAsset()
        self.ftshot = shot.FtShot(session=self.ftasset.session)
        self.ftver = asset_version.FtAssetVersion(session=self.ftasset.session)

    @property
    def entity(self):
        # type: () -> str
        """
        Selected entity type
        """
        return self.node.parm("entity").evalAsString()

    @property
    def build_name(self):
        # type: () -> str
        """
        Selected build name
        """
        return self.node.parm("build").evalAsString()

    @property
    def build_task(self):
        # type: () -> str
        """
        Selected build task
        """
        return self.node.parm("build_task").evalAsString()

    @property
    def build_cache_name(self):
        # type: () -> str
        """
        Selected build cache name
        """
        return self.node.parm("build_cache_name").evalAsString()

    @property
    def shot_cache_name(self):
        # type: () -> str
        """
        Selected shot cache name
        """
        return self.node.parm("shot_cache_name").evalAsString()

    @property
    def build_version(self):
        # type: () -> str
        """
        Selected build version
        """
        return self.node.parm("build_version").evalAsString()

    @property
    def sequence_name(self):
        # type: () -> str
        """
        Selected sequence name
        """
        return self.node.parm("sequence").evalAsString()

    @property
    def shot_name(self):
        # type: () -> str
        """
        Selected shot name
        """
        return self.node.parm("shot").evalAsString()

    @property
    def shot_task(self):
        # type: () -> str
        """
        Selected shot task
        """
        return self.node.parm("shot_task").evalAsString()

    @property
    def shot_version(self):
        # type: () -> str
        """
        Selected shot version
        """
        return self.node.parm("shot_version").evalAsString()

    @property
    def wip_or_pub(self):
        # type: () -> str
        """
        Selected wip or published mode
        """
        return hou_utils.get_menu_label(self.node, "wip_or_pub")

    @property
    def is_wip(self):
        # type: () -> bool
        """
        If the selection is wip
        """
        return bool(self.wip_or_pub == "wip")

    @property
    def is_asset(self):
        # type: () -> bool
        """
        If the selection is build
        """
        return bool(self.entity == "build")

    def build_node(self):
        """
        Build the node parameters and populate
        the asset builds and shots
        """
        self.build_parameters()
        self.populate_asset_builds()
        self.populate_sequences()

    def set_context_parameters(self):
        """
        Set the context parameters to the current environment context
        """
        if not self.ctx.task:
            return
        if self.ctx.is_asset:
            context_values = {"entity": "build",
                              "build": self.ctx.asset_build,
                              "build_task": self.ctx.task
                              }

        else:
            context_values = {"entity": "shot",
                              "sequence": self.ctx.sequence,
                              "shot": self.ctx.shot,
                              "shot_task": self.ctx.task
                              }
        for parm_name, value in context_values.items():
            hou_utils.set_menu_text(self.node, parm_name, value)

    def build_parameters(self):
        """
        Build all the parameters and based on the list
        they are in hide when condition is set
        """
        self.node.setColor(hou.Color(0.2, 0.7, 0.3))
        self.ptg = self.node.parmTemplateGroup()
        index = self.ptg.findIndices("entity")
        for menu_name in self.menu_list:
            template = self.create_menu(menu_name)

            # work out the expression when to hide the menus
            if menu_name in BUILD_LIST:
                expression = "{entity != build}"
            else:
                expression = "{entity == build}"
            template.setConditional(hou.parmCondType.HideWhen, expression)

            # add to the template
            self.ptg.insertAfter(index, template)
            index = self.ptg.findIndices(menu_name)
        self.node.setParmTemplateGroup(self.ptg)

    def create_menu(self, parm_name):
        # type: (str) -> hou.MenuParmTemplate
        """
        Create the menu item with the parameter
        name and the items list

        Args:
            parm_name: Name of the parameter to create
        """
        node_path = self.node.path()

        # get the node label from the parm name
        parm_label = parm_name.split("_")[-1].title()

        # define the command
        command = f"{COMMAND}.update_menu_items('{node_path}', '{parm_name}')"

        # create the template
        template = hou.MenuParmTemplate(parm_name,
                                        parm_label,
                                        menu_items=list(),
                                        script_callback=command,
                                        script_callback_language=hou.scriptLanguage.Python,
                                        )
        template.setConditional(hou.parmCondType.HideWhen,
                                "{entity == 0}"
                                )
        return template

    def populate_asset_builds(self):
        """
        Populate asset builds and all the sub contexts
        """
        build_names = self.ftasset.get_asset_build_names()
        hou_utils.update_menu_list(self.node, "build", build_names)
        self.update_build_tasks()
        self.update_build_cache_names()
        self.update_build_versions()
        self.update_selected_version()

    def populate_sequences(self):
        """
        Populate the sequences and all the sub contexts
        """
        sequences = self.ftshot.sequence_names
        hou_utils.update_menu_list(self.node, "sequence", sequences)
        self.update_shot_names()
        self.update_shot_tasks()
        self.update_shot_versions()
        self.update_selected_version()

    def update_shot_names(self):
        """
        Update the shot names menu list
        """
        shot_names = self.ftshot.get_shot_names(self.sequence_name)
        hou_utils.update_menu_list(self.node, "shot", shot_names)

    def update_shot_tasks(self):
        """
        Update the shot tasks menu list
        """
        task_names = self.ftshot.get_shot_task_names(self.sequence_name,
                                                     self.shot_name
                                                     )
        hou_utils.update_menu_list(self.node, "shot_task", task_names)

    def update_build_tasks(self):
        """
        Update the build tasks menu list
        """
        task_names = self.ftasset.get_asset_build_task_names(self.build_name)
        hou_utils.update_menu_list(self.node, "build_task", task_names)

    @property
    def subfolder(self):
        # type: () -> str
        """
        Based on selection the subtype folder

        Returns:
            Name of the subfolder
        """
        cache_type = self.get_cache_type()
        if cache_type == "abc":
            return cache_type
        return "cache"

    def get_root_from_context(self, overrides):
        # type: (dict) -> str
        """
        Get the root cache directory for the overrides directory

        Args:
            overrides: The selected context data

        Returns:
            root_dir: Cache root directory
        """
        ctx = context.Context(overrides=overrides)
        if self.is_wip:
            root_dir = ctx.wip_dir
        else:
            root_dir = ctx.pub_dir
        return root_dir

    @property
    def build_cache_root_dir(self):
        # type: () -> str
        """
        Get the build cache root directory
        """
        overrides = {'entity': 'build',
                     'task_name': self.build_task,
                     'asset_build_name': self.build_name,
                     'wip_or_pub': self.wip_or_pub,
                     "subfolder": self.subfolder
                     }
        root_dir = self.get_root_from_context(overrides)
        return root_dir

    @property
    def shot_cache_root_dir(self):
        # type: () -> str
        """
        From the selection get the shot cache root

        Returns:
            root_dir The shot cache root
        """
        overrides = {'entity': 'shot',
                     'sequence_name': self.sequence_name,
                     'shot_name': self.shot_name,
                     'task_name': self.shot_task,
                     'wip_or_pub': self.wip_or_pub,
                     "subfolder": self.subfolder
                     }
        root_dir = self.get_root_from_context(overrides)
        return root_dir

    def update_cache_names(self, cache_root_dir, parm_name):
        # type: (str, str) -> None
        """
        Update the names of the available caches

        Args:
            cache_root_dir: Root of the cache directories
            parm_name: Name of the parameter to update
        """
        if not os.path.exists(cache_root_dir):
            self.logger.warning(f"Directory does not exist: {cache_root_dir}")
            cache_names = list()
        else:
            cache_names = os.listdir(cache_root_dir)
            cache_names.sort()
        hou_utils.update_menu_list(self.node, parm_name, cache_names)

    def update_build_cache_names(self):
        """
        Update the build cache names
        """
        self.update_cache_names(self.build_cache_root_dir, "build_cache_name")

    def update_shot_cache_names(self):
        """
        Update the shot cache names
        """
        self.update_cache_names(self.shot_cache_root_dir, "shot_cache_name")

    def update_versions(self, cache_dir, parm_name):
        # type: (str, str) -> None
        """
        Update the menu items versions list

        Args:
            cache_dir: Path of the caches to get versions
            parm_name: Parameter name to update the versions
        """
        if not cache_dir or not os.path.exists(cache_dir):
            version_nums = list()
        else:
            version_nums = os.listdir(cache_dir)
            version_nums.sort()
            version_nums.reverse()
        hou_utils.update_menu_list(self.node, parm_name, version_nums)

    def update_shot_versions(self):
        """
        Update the available versions of the shot caches
        """
        cache_dir = os.path.join(self.shot_cache_root_dir, self.shot_cache_name)
        self.update_versions(cache_dir, "shot_version")

    def update_build_versions(self):
        """
        Update the asset build versions menu list
        """
        cache_dir = os.path.join(self.build_cache_root_dir, self.build_cache_name)
        self.update_versions(cache_dir, "build_version")

    def update_menu_items(self, node_path, parm_name):
        # type: (str, str) -> None
        """
        Update the menu items based on the changed parameter

        Args:
            node_path: Path of the node updated
            parm_name: The name of the parameter changed
        """
        self.node = hou.node(node_path)
        if parm_name == "sequence":
            self.update_shot_names()
            self.update_shot_tasks()
            self.update_shot_versions()
            self.update_selected_version()

        elif parm_name == "shot":
            self.update_shot_tasks()
            self.update_shot_cache_names()
            self.update_shot_versions()
            self.update_selected_version()

        elif parm_name == "shot_task":
            self.update_shot_cache_names()
            self.update_shot_versions()
            self.update_selected_version()

        elif parm_name == "build":
            self.update_build_tasks()
            self.update_build_cache_names()
            self.update_build_versions()
            self.update_selected_version()

        elif parm_name == "build_task":
            self.update_build_cache_names()
            self.update_build_versions()
            self.update_selected_version()

        elif parm_name == "build_cache_name":
            self.update_build_versions()
            self.update_selected_version()

        elif "version" in parm_name:
            self.update_selected_version()

    def cache_type_switch(self):
        """
        Update the node from the task down if the
        wip or cache type has been switched
        """
        node_path = self.node.path()
        if self.is_asset:
            parm_name = "build_task"
        else:
            parm_name = "shot_task"
        self.update_menu_items(node_path, parm_name)

    def get_cache_type(self):
        # type: () -> str
        """
        Get the cache type label

        Returns:
            cache_type: The cache type to create
        """
        parameter = self.node.parm("cache_type")
        labels = list(parameter.menuLabels())
        cache_type = labels[parameter.eval()]
        return cache_type

    def update_selected_version(self):
        """
        When one of the version menu items is changed get
        the selected version and update the user options.
        """
        paths = None
        if self.entity == "build":
            version_dir = os.path.join(self.build_cache_root_dir,
                                       self.build_cache_name,
                                       self.build_version
                                       )
        else:
            version_dir = os.path.join(self.shot_cache_root_dir,
                                       self.shot_cache_name,
                                       self.shot_version
                                       )

        if os.path.exists(version_dir):
            paths = os.listdir(version_dir)

        # get the selected asset version file paths
        # if paths have been found make them importable
        if not paths:
            self.node.parm("path").set("No File Found")
            self.node.parm("use_path").set("-")
        else:
            cache_path = os.path.join(version_dir, paths[0])
            self.node.parm("path").set(os.path.basename(cache_path))
            self.node.parm("use_path").set(cache_path)

    def load_selected_version_version(self):
        """
        Load the selected asset version on to the node
        """
        extension = self.get_cache_type()
        if extension != "abc":
            subnode_type = "file"
        else:
            subnode_type = "alembic"

        # set the cache path
        self.toggle_sequence_path()

        # reload the cache
        subnode = hou_utils.find_subnode_of_type(self.node, subnode_type)
        subnode.parm("reload").pressButton()

    def toggle_sequence_path(self):
        """
        Set the frame sequence based on the selection
        """
        cache_type = self.get_cache_type()
        parm_name = "fileName"

        # set the cache path
        cache_path = self.node.parm("use_path").eval()

        # convert the file path into a houdini sequence
        if cache_type != "abc":

            # use the cache parameter name
            parm_name = "file"
            seq_data = sequence_utils.get_sequence_data(cache_path)
            frame_range = self.node.parm("frame_range").evalAsString()

            # if full range use houdini format
            if frame_range == "full_range":
                cache_path = seq_data.houdini_path
            else:
                # use frame set using the formatting
                frame_number = self.node.parm("use_frame").eval()
                use_frame = str(frame_number).zfill(seq_data.padding)
                cache_path = seq_data.format_path.format(frame=use_frame)

        self.node.parm(parm_name).lock(0)
        self.node.parm(parm_name).set(cache_path)
        self.node.parm(parm_name).lock(1)

    def publish_cache(self):
        """
        Publish the cache to ftrack by using the previous data
        """
        cache_path = self.node.parm("use_path").eval()
        metadata_dir = file_utils.get_metadata_dir(cache_path)
        metadata_file = os.listdir(metadata_dir)[0]
        metadata_path = os.path.join(metadata_dir, metadata_file)
        prefix = file_utils.get_file_name(cache_path)

        job_info_dict = {"Name": f"{prefix} (Publish)",
                         "DefaultPythonHome": True
                         }
        plugin_info_dict = {"DataFilePath": metadata_path}
        custom_dict = {"prefix": prefix}
        publish_job = submit.FTrackPublishDeadlineSubmit(job_info_dict,
                                                         plugin_info_dict,
                                                         custom_dict
                                                         )
        publish_job.submit_job()
