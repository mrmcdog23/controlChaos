import maya.cmds as cmds


def create_image_plane_rig():
    cam, cam_shape = cmds.camera()
    # Create an image plane and attach it to the camera
    image_plane, image_plane_shape = cmds.imagePlane(camera=cam_shape)

    cmds.setAttr(f"{image_plane}.depth", 10)

    multiply = cmds.createNode("multiplyDivide")
    cmds.setAttr(f"{multiply}.input2Z", -1)

    locator = cmds.spaceLocator()[0]
    cmds.setAttr(f"{locator}.translateZ", -10)

    cmds.connectAttr(f"{locator}.translateZ", f"{multiply}.input1Z")
    cmds.connectAttr(f"{multiply}.outputZ", f"{image_plane}.depth")

