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
    '''
    # asset menu
    asset_menu = cmds.menuItem(label="Asset", subMenu=True, parent=no8_menu)
    cmds.menuItem(label="Asset Publisher",
                  command="import no8maya.wizard.asset_wizard as aw;aw.main()",
                  parent=asset_menu
                  )
    cmds.menuItem(label="Asset Loader",
                  command="import no8maya.asset.asset_loader as al;al.main()",
                  parent=asset_menu
                  )
    cmds.menuItem(label="Obj Import",
                  command="import no8maya.asset.obj_importer as oi;oi.ObjImporter().show()",
                  parent=asset_menu
                  )
    cmds.menuItem(label="Add Locator Attribute",
                  command="import no8maya.utils.maya_utils as mu;mu.add_locator_attribute()",
                  parent=asset_menu
                  )

    # shot menu
    shot_menu = cmds.menuItem(label="Shot", subMenu=True, parent=no8_menu)
    cmds.menuItem(label="Shot Publisher",
                  command="import no8maya.wizard.shot_wizard as sw;sw.main()",
                  parent=shot_menu
                  )
    cmds.menuItem(label="Version Manager",
                  command="import no8maya.shot.multi.version_manager as vm;vm.launch()",
                  parent=shot_menu
                  )
    cmds.menuItem(label="Set Frame Range",
                  command="import no8maya.shot.maya_shot_frame_range as msfr;msfr.main()",
                  parent=shot_menu
                  )

    cmds.menuItem(label="Object Renamer",
                  command="import no8maya.shot.renamer.object_renamer as objr;objr.main()",
                  parent=shot_menu
                  )

    # texture menu
    texture_menu = cmds.menuItem(label="Texture", subMenu=True, parent=no8_menu)
    cmds.menuItem(label="TX Manager",
                  command="import no8maya.utils.open_window as ow;ow.open_tx_manager()",
                  parent=texture_menu
                  )
    '''
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
