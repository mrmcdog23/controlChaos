""" Asset publisher in maya """
import maya.cmds as cmds
import ccmaya.maya_constants as maya_constants


RIG_GRP = maya_constants.RIG_GRP
JNT_GRP = maya_constants.JNT_GRP
GEO_GRP = maya_constants.GEO_GRP
CTLS_GRP = maya_constants.CTLS_GRP
MAIN_CTRL = maya_constants.MAIN_CTRL
ROOT_JNT = maya_constants.ROOT_JNT


def build_basic_rig():
    """
    Create a base joint and bind it to the meshes
    """
    selected_meshes = cmds.ls(sl=True)
    if not selected_meshes:
        cmds.confirmDialog(
            title=f"Nothing Selected",
            message=f"No meshes selected",
            button=['Ok']
        )
        return

    cmds.group(selected_meshes, n=GEO_GRP)

    # bind the skin cluster from the groups to the meshes
    cmds.select(cl=True)
    root_jnt = cmds.joint(n=ROOT_JNT)
    cmds.group(root_jnt, n=JNT_GRP)
    cmds.parentConstraint(ROOT_JNT, GEO_GRP)
    cmds.setAttr(f"{root_jnt}.visibility", 0)

    # work out the rig radius
    tranx1, _, tranz1, tranx2, _, tranz2 = cmds.exactWorldBoundingBox("GEO")
    valuex = tranx2 - tranx1
    valuez = tranz2 - tranz1
    circle_radius = (max([valuex, valuez]) / 2) + 1

    # create and ad control
    main_ctl = cmds.circle(n="main_ctl", nr=(0, 1, 0), r=circle_radius)
    main_ctl_shape = cmds.listRelatives(main_ctl, s=True)[0]
    cmds.setAttr(f"{main_ctl_shape}.overrideEnabled", 1)
    cmds.setAttr(f"{main_ctl_shape}.overrideColor", 17)

    # constrain the control to the joint
    cmds.pointConstraint(main_ctl, root_jnt)
    cmds.orientConstraint(main_ctl, root_jnt)

    # group the controls and rig
    cmds.group(main_ctl, n=CTLS_GRP)
    cmds.group(JNT_GRP, GEO_GRP, CTLS_GRP, n=RIG_GRP)
    cmds.select(cl=True)
