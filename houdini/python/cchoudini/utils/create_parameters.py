""" Create parameters wrapper on a node """
import hou
from typing import Optional


def int_parm(node, name, label, after_parm, join_with_next=False, min_value=None, max_value=None, cmd=None):
    # type: (hou.Node, str, str, str, Optional[bool], Optional[int], Optional[int], Optional[str]) -> None
    """
    When a node is created add the submit to deadline button

    Args:
        node: The houdini node to add to
        name: Parameter name
        label: Display text
        after_parm: Name of parameter to add after
        join_with_next: Whether to join the next
        min_value: The minimum value
        max_value: The maximum value
        cmd: Python command to run
    """
    min_value = min_value or 1
    max_value = max_value or 30
    template = hou.IntParmTemplate(
        name, label, 1,  min=min_value, max=max_value,
        default_value=(1,),
        join_with_next=join_with_next,
        script_callback=cmd,
        script_callback_language=hou.scriptLanguage.Python
    )
    add_to_template(node, after_parm, template)


def float_parm(node, name, label, after_parm, join_with_next=False, cmd=None):
    # type: (hou.Node, str, str, str, Optional[bool], Optional[str]) -> None
    """
    When a node is created add the submit to deadline button

    Args:
        node: The houdini node to add to
        name: Parameter name
        label: Display text
        after_parm: Name of parameter to add after
        join_with_next: Whether to join the next
        cmd: Python command to run
    """
    template = hou.FloatParmTemplate(
        name, label, 1,
        join_with_next=join_with_next,
        script_callback=cmd,
        script_callback_language=hou.scriptLanguage.Python
    )
    add_to_template(node, after_parm, template)


def string_parm(node, name, label, after_parm, join_with_next=False, hide=False, value=None):
    # type: (hou.Node, str, str, str, Optional[bool], Optional[bool], Optional[str]) -> None
    """
    When a node is created add the submit to deadline button

    Args:
        node: The houdini node to add to
        name: Parameter name
        label: Display text
        after_parm: Name of parameter to add after
        join_with_next: Whether to join the next
        hide: Whether to hide the parameter
        value: The default string value
    """
    num_components = 1
    default_value = value or str()
    template = hou.StringParmTemplate(
        name,
        label,
        num_components,
        join_with_next=join_with_next,
        is_hidden=hide,
        is_label_hidden=hide,
        default_value=(default_value,),
    )
    add_to_template(node, after_parm, template)


def button_parm(node, name, label, after_parm, command):
    # type: (hou.Node, str, str, str, str) -> None
    """
    Button parameter to create

    Args:
        node: The houdini node to add to
        name: Parameter name
        label: Display text
        after_parm: Name of parameter to add after
        command: Python function to run
    """
    template = hou.ButtonParmTemplate(
        name,
        label,
        script_callback=command,
        script_callback_language=hou.scriptLanguage.Python,
    )
    add_to_template(node, after_parm, template)


def menu_parm(node, name, label, after_parm, items_list, command=None):
    # type: (hou.Node, str, str, str, list[str], Optional[str]) -> None
    """
    Create a menu parameter

    Args:
        node: The houdini node to add to
        name: Parameter name
        label: Display text
        after_parm: Name of parameter to add after
        items_list: List of menu items
        command: Python function to run
    """
    template = hou.MenuParmTemplate(
        name,
        label,
        menu_items=items_list,
        menu_labels=items_list,
        script_callback=command,
        script_callback_language=hou.scriptLanguage.Python,
    )
    add_to_template(node, after_parm, template)


def float_vector3_parm(node, name, label, after_parm, cmd=None):
    # type: (hou.Node, str, str, str, Optional[str]) -> None
    """
    Create a menu parameter

    Args:
        node: The houdini node to add to
        name: Parameter name
        label: Display text
        after_parm: Name of parameter to add after
        cmd: Python function to run
    """
    template = hou.FloatParmTemplate(
        name=name,
        label=label,
        num_components=3,
        naming_scheme=hou.parmNamingScheme.XYZW,
        default_value=(0.0, 0.0, 0.0),
        min=0.0,
        max=1.0,
        script_callback=cmd,
        script_callback_language=hou.scriptLanguage.Python
    )
    add_to_template(node, after_parm, template)


def toggle_parm(node, name, label, after_parm, cmd=None):
    # Create a float vector3 parameter template
    template = hou.ToggleParmTemplate(
        name=name,
        label=label,
        script_callback=cmd,
        script_callback_language=hou.scriptLanguage.Python
    )
    add_to_template(node, after_parm, template)


def add_to_template(node, after_parm, template):
    # type: (hou.Node, str, hou.ParmTemplate) -> None
    """
    Create a menu parameter

    Args:
        node: The houdini node to add to
        after_parm: Name of parameter to add after
        template:
    """
    ptg = node.parmTemplateGroup()
    index = ptg.findIndices(after_parm)
    ptg.insertAfter(index, template)
    node.setParmTemplateGroup(ptg)

