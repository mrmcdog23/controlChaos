""" Add to the USD Render Rop """
import hou


def set_usdrender_rop(usdrender_rop_node):
    # type: (hou.Node) -> None
    """
    Create the submit to deadline button

    Args:
        usdrender_rop_node: The usd render node to add to
    """
    ptg = usdrender_rop_node.parmTemplateGroup()
    index = ptg.findIndices("execute")
    command = "import cchoudini.wizard.usd_render_wizard as urw;urw.main(hou.pwd())"
    button = hou.ButtonParmTemplate(
        "deadline_submit",
        "Render Submit to Deadline",
        script_callback=command,
        script_callback_language=hou.scriptLanguage.Python,
    )
    ptg.insertAfter(index, button)
    usdrender_rop_node.setParmTemplateGroup(ptg)


node = kwargs['node']
set_usdrender_rop(node)
