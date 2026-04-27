import maya.cmds as cmds


def image_plane_to_mesh():
    ip_transform = cmds.ls(sl=True)[0]
    ip = cmds.listRelatives(ip_transform, s=True)[0]

    width = cmds.getAttr(f"{ip}.width")
    height = cmds.getAttr(f"{ip}.height")
    img = cmds.getAttr(f"{ip}.imageName")
    tx = cmds.xform(ip_transform, q=True, ws=True, translation=True)
    rot = cmds.xform(ip_transform, q=True, ws=True, rotation=True)
    scl = cmds.xform(ip_transform, q=True, ws=True, scale=True)

    plane, _ = cmds.polyPlane(
        name="imagePlane_mesh",
        w=width, h=height,
        sx=1, sy=1,
        ax=(0, 0, 1)
    )

    cmds.xform(plane, ws=True, translation=tx)
    cmds.xform(plane, ws=True, rotation=rot)
    cmds.xform(plane, ws=True, scale=scl)

    if img:
        shader = cmds.shadingNode("lambert", asShader=True, name="imagePlane_mat")
        sg = cmds.sets(
            renderable=True,
            noSurfaceShader=True,
            name="imagePlane_matSG"
        )
        file_nd = cmds.shadingNode("file", asTexture=True, name="imagePlane_tex")
        p2d = cmds.shadingNode("place2dTexture", asUtility=True)

        cmds.connectAttr(f"{p2d}.outUV", f"{file_nd}.uv")
        cmds.connectAttr(f"{p2d}.outUvFilterSize", f"{file_nd}.uvFilterSize")
        cmds.setAttr(f"{file_nd}.fileTextureName", img, type="string")
        cmds.connectAttr(f"{file_nd}.outColor", f"{shader}.color")
        cmds.connectAttr(f"{shader}.outColor", f"{sg}.surfaceShader")
        cmds.sets(plane, edit=True, forceElement=sg)

    cmds.select(plane)
    return plane


def set_channel_state(obj, attrs):
    """
    Low-level: set keyable / lock / channelBox flags on attrs.
    Hiding from the channel box = keyable=False, channelBox=False.
    """
    for attr in attrs:
        full = f"{obj}.{attr}"
        if not cmds.objExists(full):
            continue
        cmds.setAttr(full, lock=True)
        cmds.setAttr(full, keyable=False, channelBox=False)


def create_image_plane_rig():
    cam, cam_shape = cmds.camera()

    # Create an image plane and attach it to the camera
    image_plane, image_plane_shape = cmds.imagePlane(camera=cam_shape)
    cmds.setAttr(f"{image_plane}.depth", 10)

    # create the depth locator
    depth_loc = cmds.spaceLocator(n="depth")[0]
    cmds.parent(depth_loc, cam)
    cmds.setAttr(f"{depth_loc}.translateZ", -10)
    cmds.setAttr(f"{depth_loc}.localScale", 0.5, 0.5, 0.5, type="double3")

    # create the depth node
    depth_node = cmds.createNode("multiplyDivide", n="depth_node")
    cmds.setAttr(f"{depth_node}.input2Z", -1)

    # connect the depth and locator nodes
    cmds.connectAttr(f"{depth_loc}.translateZ", f"{depth_node}.input1Z")
    cmds.connectAttr(f"{depth_node}.outputZ", f"{image_plane}.depth")

    # the scale of the locator is dependent on the depth
    cmds.connectAttr(f"{depth_loc}.translateZ", f"{depth_loc}.scaleX")
    cmds.connectAttr(f"{depth_loc}.translateZ", f"{depth_loc}.scaleY")
    cmds.connectAttr(f"{depth_loc}.translateZ", f"{depth_loc}.scaleZ")

    hide_depth_channels = ["tx", "ty", "rx", "ry", "rz", "sx", "sy", "sz", "v"]
    set_channel_state(depth_loc, hide_depth_channels)


    # create offset locator for rotations and X/Y translations
    offset_loc = cmds.spaceLocator(n="offset")[0]
    cmds.setAttr(f"{offset_loc}.translateZ", -10)
    cmds.setAttr(f"{offset_loc}.localScale", 0.5, 0.5, 0.5, type="double3")
    cmds.parent(offset_loc, depth_loc)
    cmds.setAttr(f"{offset_loc}.translateZ", l=True)

    # invert and set the rotations
    offset_node = cmds.createNode("multiplyDivide", n="offset_node")

    # set the rotations
    cmds.connectAttr(f"{offset_loc}.rotateZ", f"{offset_node}.input1Z")
    cmds.connectAttr(f"{offset_node}.outputZ", f"{image_plane_shape}.rotate")
    cmds.setAttr(f"{offset_node}.input2Z", -1)

    # set the X translations
    cmds.connectAttr(f"{offset_loc}.translateX", f"{offset_node}.input1X")
    cmds.connectAttr(f"{offset_node}.outputX", f"{image_plane_shape}.offsetX")
    cmds.setAttr(f"{offset_node}.input2X", -1.378)

    # set the Y translations
    cmds.connectAttr(f"{offset_loc}.translateY", f"{offset_node}.input1Y")
    cmds.connectAttr(f"{offset_node}.outputY", f"{image_plane_shape}.offsetY")
    cmds.setAttr(f"{offset_node}.input2Y", -1.378)

    hide_offset_channels = ["tz", "rx", "ry", "sx", "sy", "sz", "v"]
    set_channel_state(offset_loc, hide_offset_channels)



