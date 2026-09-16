""" Add to the Arnold Render Settings node """
import hou


def set_render_settings(render_settings_node):
    # type: (hou.Node) -> None
    """
    Create the update path to deadline button

    Args:
        render_settings_node: The Arnold render settings to add to
    """
    ptg = render_settings_node.parmTemplateGroup()
    index = ptg.findIndices("productName")
    command = "import cchoudini.node.usdrender_rop_node as urn;" \
              "urn.USDRenderRopNode(render_settings_node=hou.pwd())" \
              ".set_render_settings_node_path()"
    button = hou.ButtonParmTemplate(
        "set_output_path",
        "Set Output Path",
        script_callback=command,
        script_callback_language=hou.scriptLanguage.Python,
    )
    ptg.insertBefore(index, button)
    render_settings_node.setParmTemplateGroup(ptg)


node = kwargs['node']
set_render_settings(node)

