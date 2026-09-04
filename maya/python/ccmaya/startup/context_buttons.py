""" Class to set the environment context """
import os
import maya.cmds as cmds
import maya.mel as mel
import ccftrack.shot as shot
import ccftrack.asset as asset
import cccore.file_env.context as context
import cccore.utils.file_utils as file_utils
import cccore.file_env.context_utils as context_utils
import cccore.data.server_data as server_data
import cccore.file_env.ctx_constants as ctx_constants
import ccmaya.panels.maya_context_panel as maya_context_panel
import ccmaya.utils.maya_utils as maya_utils
from CCPySide import QtWidgets
from typing import Optional


# button sizes
BUTTON_HEIGHT = 33
MARGIN = 3
STARTING = 480
FTRACK_SHOT = shot.FtShot()
FTRACK_ASSET = asset.FtAsset(session=FTRACK_SHOT.session)


class ContextButtons(object):
    """
    Create button in maya for setting the context
    """
    def __init__(self):
        self.toolBox = mel.eval("setParent $gToolboxForm;")
        self.project_data = server_data.ProjectData()

    def get_entity_type(self, entity_name):
        # type: (str) -> None
        """
        Create either the shot or asset buttons based on the entity type

        Args:
            entity_name: Name of the selected entity
        """
        # reset variables
        all_variables = ctx_constants.ASSET_ORDER + ctx_constants.SHOT_ORDER
        for variable in all_variables:
            if os.environ.get(variable):
                del os.environ[variable]

        os.environ["entity"] = entity_name
        if entity_name == "asset":
            self.asset_types_btn()
        else:
            self.sequence_list_btn()
        try:
            cmds.button(entity_btn, e=True, l=entity_name)
        except NameError:
            pass

    @staticmethod
    def remove_btn_list(btn_list):
        # type: (list[str]) -> None
        """
        find all the names of the buttons that are
        under the button to create and remove them

        Args:
            btn_list: List of button names to delete
        """
        for lower_button in btn_list:
            if lower_button == ctx_constants.ENTITY:
                continue
            lower_btn_name = f"btn_{lower_button}"
            if cmds.button(lower_btn_name, ex=True):
                cmds.deleteUI(lower_btn_name, control=True)

    def create_btn(self, text, add_list, cmd_format):
        # type: (str, list[str], str) -> cmds.button
        """
        Create the button to display

        Args:
            text: Text displayed on the button
            add_list: List of items to add
            cmd_format: Text command format

        Returns:
            btn: Button created
        """
        entity_type = os.environ.get(ctx_constants.ENTITY, ctx_constants.BUILD)

        # remove previous buttons it could be switched entity
        if entity_type == ctx_constants.BUILD:
            use_list = ctx_constants.ASSET_ORDER[:]
            self.remove_btn_list(ctx_constants.SHOT_ORDER)
        else:
            use_list = ctx_constants.SHOT_ORDER[:]
            self.remove_btn_list(ctx_constants.ASSET_ORDER)

        # remove any potential buttons under the one created
        index = use_list.index(text)
        remove_lower = use_list[index:]
        self.remove_btn_list(remove_lower)

        # work out button position based on the index in the list
        position = STARTING + ((BUTTON_HEIGHT + MARGIN) * index)

        # create the button and attach it to the layout
        btn_name = f"btn_{text}"

        # use end of text for the asset build and type
        label = context_utils.get_btn_label(text)
        btn = cmds.button(btn_name, l=label, w=38, h=BUTTON_HEIGHT, rs=False)
        cmds.formLayout(self.toolBox, edit=1, attachForm=[(btn, 'top', position)])

        # populate the popup menu
        pop_menu = cmds.popupMenu(button=1)
        cmds.setParent(pop_menu, menu=True)

        if not add_list:
            add_list = ["No Items"]
        for add_text in add_list:
            btn_cmd = cmd_format.format(ctx_constants.CONTEXT_BTNS, add_text)
            cmds.menuItem(l=add_text, c=btn_cmd)
        return btn

    def set_btn_text(self, envvar, btn, text):
        # type: (str, cmds.button, str) -> None
        """
        Set the button text and its environment variable

        Args:
            envvar: Name of the environment variable
            btn: The button to set
            text: The value to set the var and button to
        """
        display_text = context_utils.get_display_text(envvar, text)
        cmds.button(btn, e=True, l=display_text)
        os.environ[envvar] = text

    def entity_button(self):
        """
        Create main entity button for selecting either asset or shot
        """
        global entity_btn
        cmd_format = '{0};ctx.get_entity_type("{1}")'
        entity_btn = self.create_btn(ctx_constants.ENTITY,
                                     ctx_constants.ENTITIES,
                                     cmd_format
                                     )

    def asset_types_btn(self):
        """
        Create the asset names button
        """
        global asset_types_btn
        asset_build_types_names = FTRACK_ASSET.asset_build_types_names
        cmd_format = '{0};ctx.asset_names_btn("{1}")'
        asset_types_btn = self.create_btn(ctx_constants.ASSET_BUILD_TYPE_NAME,
                                          asset_build_types_names,
                                          cmd_format
                                          )

    def asset_names_btn(self, asset_type):
        """
        Create the asset names button
        """
        global asset_names_btn
        self.set_btn_text(ctx_constants.ASSET_BUILD_TYPE_NAME, asset_types_btn, asset_type)
        asset_names = FTRACK_ASSET.get_asset_build_names(asset_type=asset_type)
        cmd_format = '{0};ctx.asset_task_btn("{1}")'
        asset_names_btn = self.create_btn(ctx_constants.ASSET_BUILD_NAME,
                                          asset_names,
                                          cmd_format
                                          )

    def asset_task_btn(self, asset_name):
        # type: (str) -> None
        """
        Create the asset tasks button

        Args:
            asset_name: The selected asset name
        """
        global task_btn
        self.set_btn_text(ctx_constants.ASSET_BUILD_NAME,
                          asset_names_btn,
                          asset_name
                          )
        task_names = FTRACK_ASSET.get_asset_build_task_names(asset_name)
        cmd_format = '{0};ctx.set_asset_task("{1}")'
        task_btn = self.create_btn(ctx_constants.TASK_NAME,
                                   task_names,
                                   cmd_format
                                   )

    def set_asset_task(self, task):
        # type: (str) -> None
        """
        Set the asset button task

        Args:
            task: Name of the task to set the project to.
        """
        self.set_btn_text(ctx_constants.TASK_NAME, task_btn, task)
        self.set_project()
        self.update_context_panel()

    def episode_list_btn(self):
        """
        Set the episode list button
        """
        global episode_btn
        episode_names = FTRACK_SHOT.episode_names
        cmd_format = '{0};ctx.sequence_list_btn("{1}")'
        episode_btn = self.create_btn(ctx_constants.EPISODE_NAME,
                                      episode_names,
                                      cmd_format
                                      )

    def sequence_list_btn(self, episode=None):
        # type: (Optional[str]) -> None
        """
        Set the sequence list button

        Args:
            episode: Name of the selected episode
        """
        global sequence_btn
        if episode:
            FTRACK_SHOT.episode_name = episode
            self.set_btn_text(ctx_constants.EPISODE_NAME, episode_btn, episode)
        sequence_names = FTRACK_SHOT.sequence_names
        cmd_format = '{0};ctx.shot_list_btn("{1}")'
        sequence_btn = self.create_btn(ctx_constants.SEQUENCE_NAME,
                                       sequence_names,
                                       cmd_format
                                       )

    def shot_list_btn(self, sequence):
        # type: (str) -> None
        """
        Create the shot list button

        Args:
            sequence: Name of the selected sequence
        """
        global shot_btn
        self.set_btn_text(ctx_constants.SEQUENCE_NAME, sequence_btn, sequence)
        shot_names = FTRACK_SHOT.get_shot_names(sequence)
        cmd_format = '{0};ctx.shot_task_btn("{1}")'
        shot_btn = self.create_btn(ctx_constants.SHOT_NAME,
                                   shot_names,
                                   cmd_format
                                   )

    def shot_task_btn(self, shot_name):
        # type: (str) -> None
        """
        Create the shot task button

        Args:
            shot_name: Name of the selected shot
        """
        global task_btn
        self.set_btn_text(ctx_constants.SHOT_NAME, shot_btn, shot_name)
        sequence_name = os.environ["sequence_name"]
        task_names = FTRACK_SHOT.get_shot_task_names(sequence_name, shot_name)
        cmd_format = '{0};ctx.set_shot_task("{1}")'
        task_btn = self.create_btn(ctx_constants.TASK_NAME,
                                   task_names,
                                   cmd_format
                                   )

    def set_shot_task(self, task):
        # type: (str) -> None
        """
        Set the task list button text

        Args:
            task: Name of the selected task
        """
        self.set_btn_text(ctx_constants.TASK_NAME, task_btn, task)
        self.set_project()
        self.update_context_panel()

    @staticmethod
    def set_project():
        """
        Set the maya project workspace
        """
        ctx = context.Context()
        if not os.path.exists(ctx.user_dir):
            file_utils.create_directories(ctx.user_dir)
        mel.eval(f'setProject "{ctx.user_dir}"')

    @staticmethod
    def update_context_panel():
        """
        Create and update the version of the cc panel
        """
        maya_context_panel.create_cc_panel()
        maya_window = maya_utils.get_maya_main_window()

        # get the context panel populate the versions
        ctx_panel = maya_window.findChild(QtWidgets.QWidget, ctx_constants.CONTEXT_PANEL)
        if ctx_panel:
            ctx_panel.populate_wip_versions()
