"""
Basic three-point light rig (key / fill / rim) plus optional soft skydome
for Maya + Arnold. Run in the Script Editor (Python tab).
"""
import maya.cmds as cmds
import mtoa.utils as mutils
import ccmaya.utils.maya_utils as maya_utils
import ccmaya.render.create_playblast as create_playblast
import cccore.utils.cc_logging as cc_logging


# constants
OBJ_START = 1
OBJ_END = 100
CAM_START = 101
CAM_END = 200
HEIGHT = 540
WIDTH = 1024


class MakeTurntableRender(object):
    def __init__(self, data):
        self.data = data
        self.logging = cc_logging.cc_logger()
        self.top_node = maya_utils.get_asset_top_node()

        self.snap_object_to_center()
        self.set_object_pivot_and_rotations()
        self.set_frame_range()
        self.create_render_camera()
        self.build_three_point_rig()
        self.create_render()

    def snap_object_to_center(self):
        """
        Snap the object to the origin
        """
        cmds.select(self.top_node)
        cmds.xform(cpc=True)
        loc = cmds.spaceLocator()[0]
        cmds.pointConstraint(loc, self.top_node)
        cmds.delete(loc)

    def set_object_pivot_and_rotations(self):
        """
        Move the object to be on the base
        """
        _, bbminy, _ = cmds.getAttr(f"{self.top_node}.boundingBoxMin")[0]
        _, transy, _ = cmds.getAttr(f"{self.top_node}.translate")[0]
        diff = (bbminy - transy) * -1
        cmds.setAttr(f"{self.top_node}.ty", diff)

        # set the object pivot to the center
        cmds.select(self.top_node)
        cmds.xform(worldSpace=True, pivots=(0, 0, 0))
        cmds.select(cl=True)

    def set_frame_range(self):
        """
        Set the start and end frame animation and time slider
        """
        cmds.setKeyframe(self.top_node, v=0, t=OBJ_START, at='rotateY')
        cmds.setKeyframe(self.top_node, v=360, t=OBJ_END + 1, at='rotateY')
        cmds.playbackOptions(min=OBJ_START, ast=OBJ_START, max=CAM_END, aet=CAM_END)

    def create_render_camera(self):
        """
        Create the turntable of the asset
        """
        cam, cam_shape = cmds.camera()
        cmds.viewFit(cam_shape, all=True)
        cmds.setAttr(f"{cam_shape}.panZoomEnabled", True)
        cmds.setAttr(f"{cam_shape}.renderPanZoom", True)
        cmds.setAttr(f"{cam_shape}.zoom", 1.2)

        camera_group = cmds.group(cam, n="camera_group")
        cmds.xform(camera_group, pivots=(0, 0, 0), worldSpace=True)
        cmds.setKeyframe(camera_group, v=0, t=CAM_START, at='rotateY')
        cmds.setKeyframe(camera_group, v=360, t=CAM_END + 1, at='rotateY')

    def create_ai_light(self, node_type, name):
        """
        Create an Arnold light and return (transform, shape).
        Handles mtoa returning the (shape, transform) pair in either order.
        """
        result = mutils.createLocator(node_type, asLight=True)
        shape = next(n for n in result if cmds.nodeType(n) == node_type)
        transform = next(n for n in result if n != shape)
        transform = cmds.rename(transform, name)
        shape = cmds.listRelatives(transform, shapes=True)[0]
        return transform, shape

    def make_area_light(self, name, position, target, exposure, color=(1, 1, 1), size=4, samples=3):
        """
        Quad area light placed at `position`, aimed at `target`.
        """
        xform, shape = self.create_ai_light("aiAreaLight", name)
        cmds.setAttr(shape + ".exposure", exposure)
        cmds.setAttr(shape + ".color", *color, type="double3")
        cmds.setAttr(shape + ".aiSamples", samples)
        cmds.setAttr(xform + ".scale", size, size, size)
        cmds.move(*position, xform)

        # Area lights emit along -Z, so aim -Z at the target, then bake the rotation
        aim = cmds.aimConstraint(target, xform, aimVector=(0, 0, -1), upVector=(0, 1, 0))
        cmds.delete(aim)
        return xform

    @property
    def is_arnold_render(self):
        # type: () -> bool
        """ If it is an arnold render """
        return self.data["renderer"] == "arnold"

    def build_three_point_rig(self):#
        """
        If it is an arnold render then create a light rig
        """
        if not self.is_arnold_render:
            return

        target_pos=(0, 2, 0)
        distance=10
        add_skydome=True

        tx, ty, tz = target_pos
        target = cmds.spaceLocator(name="lightTarget")[0]
        cmds.move(tx, ty, tz, target)

        # main light: front-left, above, warm, strongest
        key = self.make_area_light(          # main light: front-left, above, warm, strongest
            "key_light", (tx - distance * 0.7, ty + distance * 0.7, tz + distance * 0.7),
            target, exposure=7, color=(1.0, 0.95, 0.85), size=4)

        # softens shadows: front-right, lower, cool, dimmer
        fill = self.make_area_light(
            "fill_light", (tx + distance * 0.8, ty + distance * 0.3, tz + distance * 0.5),
            target, exposure=5, color=(0.85, 0.92, 1.0), size=6)

        # separates subject from background: behind, high
        rim = self.make_area_light(
            "rim_light", (tx + distance * 0.3, ty + distance * 0.8, tz - distance * 0.9),
            target, exposure=7, color=(1.0, 1.0, 1.0), size=3)
        lights = [key, fill, rim]

        # low-level ambient so shadows aren't pitch black
        if add_skydome:
            sky, sky_shape = self.create_ai_light("aiSkyDomeLight", "ambient_sky")
            cmds.setAttr(sky_shape + ".intensity", 0.15)
            lights.append(sky)

        cmds.delete(target)
        grp = cmds.group(lights, name="lightRig_grp")
        self.logging.info("Light rig created")
        return grp

    def create_render(self):
        """
        Create the render and make the movie from it
        """
        render_data = {
            "start_frame": OBJ_START,
            "end_frame": CAM_END,
            "name": self.data["asset_build_name"],
            "height": HEIGHT,
            "width": WIDTH,
            "renderer": self.data["renderer"]
        }
        playblast_cls = create_playblast.PlayblastScene(render_data=render_data)
        playblast_cls.create_images()

        self.movie_path = playblast_cls.temp_mov_path
        self.logging.info(f"Created: {self.movie_path}")
