""" Set the expression on karma nodes on creation """
import hou


# the expressions constants
JOB_VER_EXP = '$JOB + "/houdini/render/" + $TASK + "/$VER/"' \
              ' + strreplace($HIPNAME, $VER, "") + $OS + "_" + $VER + ".$F4.exr"'


def set_mantra_rop(node):
    """
    Set the mantra output expression

    Args:
        node (hou.Node): The mantra rop node
    """
    # output expression swapping the file name version
    # with the rop name so the version is at the end
    node.parm("picture").setExpression(JOB_VER_EXP,
                                       language=hou.exprLanguage.Hscript,
                                       replace_expression=True
                                       )


mantra_node = kwargs['node']
set_mantra_rop(mantra_node)
