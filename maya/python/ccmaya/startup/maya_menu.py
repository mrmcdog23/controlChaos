""" Build the maya menu for No8 """
import maya.cmds as cmds
import maya.mel as mel


def build_cc_menu():
    """
    Build the menu with No8 specific tools
    """
    cc_menu = cmds.menu(
        "ccMenu",
        label="Control Chaos",
        parent=mel.eval("$retvalue = $gMainWindow;"),
    )

    # asset menu
    asset_menu = cmds.menuItem(label="Asset", subMenu=True, parent=cc_menu)
    cmds.menuItem(label="Asset Loader",
                  command="import ccmaya.asset.asset_loader as al;al.main()",
                  parent=asset_menu
                  )

    # shot menu
    shot_menu = cmds.menuItem(label="Shot", subMenu=True, parent=cc_menu)
    cmds.menuItem(label="Shot Loader",
                  command="import ccmaya.shot.loader.maya_load_shot as msl;msl.main()",
                  parent=shot_menu
                  )

    # reload modules
    cmds.menuItem(divider=True, parent=cc_menu)
    cmds.menuItem(label="Reload Modules",
                  command="import cccore.utils.file_utils as fu;fu.reload_cc_modules()",
                  parent=cc_menu
                  )


def build_cc_playblast_menu():
    """
    Added the ccplayblast command to the Timeline popup menu.
    """
    mel.eval("""updateTimeSliderMenu TimeSliderMenu""")
    if cmds.menuItem("cc_playblast_item", exists=True):
        cmds.deleteUI("cc_playblast_item")

    if cmds.menuItem("cc_playblast_item_option", exists=True):
        cmds.deleteUI("cc_playblast_item_option")

    cmds.menuItem("cc_playblast_item",
                  label="Control Chaos Playblast...",
                  command="import ccmaya.shot.playblaster.playblast_wizard as pbwz;pbwz.main()",
                  ia="timeSliderPlayblastOptionItem",
                  p="TimeSliderMenu"
                  )
