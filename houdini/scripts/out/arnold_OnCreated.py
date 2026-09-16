""" Run code when an arnold rop is created """
import hou
import cchoudini.utils.node_utils as node_utils


# the expressions constants
ASS_EXP = '$JOB + "/houdini/archive/" + $HIPNAME + "_" + $OS + ".$F4.ass"'
PICTURE_EXPRESSION = ('$JOB + "/houdini/render/$TASK/$RENDER_VERSION/$OS/" + '
                      '$RENDER_PREFIX + $OS + "_" + $RENDER_VERSION + ".$F4.exr"')


def set_arnold_rop(node):
    """
    Set the arnold output expression

    Args:
        node (hou.Node): The arnold rop node
    """
    # output expression swapping the file name version
    # with the rop name so the version is at the end
    node.parm("ar_picture").setExpression(PICTURE_EXPRESSION,
                                          replace_expression=True
                                          )
    node.parm("ar_ass_export_enable").set(1)
    node.parm("ar_ass_file").setExpression(ASS_EXP,
                                           language=hou.exprLanguage.Hscript,
                                           replace_expression=True
                                           )
    node.parm("trange").set(1)


arnold_node = kwargs['node']
set_arnold_rop(arnold_node)


node_utils.create_render_random_frames_parm(arnold_node)
