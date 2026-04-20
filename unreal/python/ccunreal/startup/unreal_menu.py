""" Create custom menu for Control Chaos tools """
import unreal as ue


def create_submenu(menu, label):
    # type: (ue.ToolMenuEntry, str) -> ue.ToolMenuEntry
    """
    Create a sub menu item

    Args:
        menu: The parent menu to add to
        label: Text for the sub menu

    Returns:
        New sub menu
    """
    return menu.add_sub_menu(menu.get_name(), label, label, label)


def add_separator(menu):
    """
    Create a separator to the menu

    Args:
        menu (ue.ToolMenuEntry): The parent menu to add to
    """
    separator = ue.ToolMenuEntry(type=ue.MultiBlockType.SEPARATOR)
    menu.add_menu_entry(menu.get_name(), separator)


def create_command(menu, label, command):
    # type: (ue.ToolMenuEntry, str, str) -> None
    """
    Create an item that triggers a command

    Args:
        menu: The parent menu to add to
        label: Text for the item
        command: Python command to run when clicked
    """
    item = ue.ToolMenuEntry(name=label, type=ue.MultiBlockType.MENU_ENTRY)
    item.set_string_command(ue.ToolMenuStringCommandType.PYTHON,
                            custom_type="rrr",
                            string=command
                            )
    item.set_label(label)
    menu.add_menu_entry("Items", item)


def main():
    """
    Build control chaos menu unreal menu
    """
    menus = ue.ToolMenus.get()
    main_menu = menus.find_menu("LevelEditor.MainMenu")
    control_chaos_menu = create_submenu(main_menu, "Control Chaos")

    # shot menu
    shot_menu = create_submenu(control_chaos_menu, "Shot")
    command = "import ccunreal.shot.import_fbx_cam as ifc;ifc.launch()"
    create_command(shot_menu, "Load FBX Cameras", command)

    add_separator(control_chaos_menu)

    # pipeline menu
    command = "import cccore.utils.file_utils as fu;fu.reload_cc_modules()"
    create_command(control_chaos_menu, "Reload Modules", command)

    # refresh the menus
    menus.refresh_all_widgets()


main()
