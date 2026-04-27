""" Convert an image plane to a mesh """
import math
import maya.cmds as cmds
import maya.api.OpenMaya as om


BUFFER = 1.42


def get_image_plane_corners_cmds(image_plane_shape, camera_shape):
    """
    Fallback using cmds attributes + camera local space transform.
    """
    depth    = cmds.getAttr(f"{image_plane_shape}.depth")

    # ── Pull camera optics ────────────────────────────────────────────────────
    focal_length   = cmds.getAttr(f"{camera_shape}.focalLength")       # mm
    film_aperture  = cmds.getAttr(f"{camera_shape}.horizontalFilmAperture") * 25.4
    multi = (depth * -1) / ((focal_length / film_aperture) * BUFFER)

    # get the image plane shapes data
    width = cmds.getAttr(f"{image_plane_shape}.sizeX") * multi
    height = cmds.getAttr(f"{image_plane_shape}.sizeY") * multi
    offset_x = cmds.getAttr(f"{image_plane_shape}.offsetX")* (multi * -1)
    offset_y = cmds.getAttr(f"{image_plane_shape}.offsetY")* (multi * -1)
    depth = cmds.getAttr(f"{image_plane_shape}.depth")

    half_w = width  / 2.0
    half_h = height / 2.0

    # Image plane's own rotation (degrees, around its center, in the camera's XY plane)
    rotation_deg = cmds.getAttr(f"{image_plane_shape}.rotate") * -1
    rotation_rad = om.MAngle(rotation_deg, om.MAngle.kDegrees).asRadians()
    cos_r = math.cos(rotation_rad)
    sin_r = math.sin(rotation_rad)

    def rotate_corner(x, y):
        """
        Rotate point (x, y) around the offset center by the plane's rotation.
        """
        # Rotate around the offset centre, not the origin
        rx = cos_r * x - sin_r * y
        ry = sin_r * x + cos_r * y
        return rx, ry

    # Camera looks down -Z in local space, so the plane sits at z = -depth.
    raw_corners = [
        (-half_w, -half_h),   # BL
        ( half_w, -half_h),   # BR
        (-half_w,  half_h),   # TL
        ( half_w,  half_h),   # TR
    ]
    local_corners = [
        om.MPoint(rx + offset_x, ry + offset_y, -depth)
        for (x, y) in raw_corners
        for rx, ry in [rotate_corner(x, y)]
    ]

    # get the world matrix of the image plane
    sel = om.MSelectionList()
    sel.add(image_plane_shape)
    dag = sel.getDagPath(0)
    world_matrix = dag.inclusiveMatrix()

    # work out the corner points
    world_corners = [p * world_matrix for p in local_corners]
    return world_corners


def convert_to_mesh():
    """
    Convert the selected image plane to the mesh
    """
    # get the camera from selection
    try:
        cam_transform = cmds.ls(sl=True)[0]
    except IndexError:
        cmds.warning("Nothing selected")
        return

    # get the camera and image plane shape
    camera_shape = cmds.listRelatives(cam_transform, s=True)[0]
    ip_transform = cmds.listConnections(camera_shape, type="imagePlane")[0]
    ip_shape = cmds.listRelatives(ip_transform, s=True)[0]

    # create a mesh and get start and end frame
    mesh_plane = cmds.polyPlane(sx=1, sy=1)[0]
    start_frame = int(cmds.playbackOptions(q=True, min=True))
    end_frame = int(cmds.playbackOptions(q=True, max=True))

    # build set of the vertexes to bake
    vertex_key_set = set()
    for index in range(0, 4):
        vertex_key_set.add(f"{mesh_plane}.vtx[{index}]")

    # step through each frame and snap the vertexes to the
    # corners of the image plane and set the keyframes
    for frame_num in range(start_frame, end_frame+1):
        cmds.currentTime(frame_num, e=True)
        corners = get_image_plane_corners_cmds(ip_shape, camera_shape)

        # snap the vertex to the image plane corners
        for index, pt in enumerate(corners):
            cmds.xform(
                f"{mesh_plane}.vtx[{index}]",
                translation=(pt.x, pt.y, pt.z),
                worldSpace=True
            )
            cmds.setKeyframe(vertex_key_set)
