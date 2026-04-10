""" Control chaos hud node for camera information """
import sys
import math
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.api.OpenMayaRender as omr
import maya.api.OpenMayaAnim as omanim
import maya.cmds as cmds


# plugin information
PLUGIN_VERSION = '1.0.0'
NODE_NAME = 'controlChaosHUD'
NODE_ID = om.MTypeId(0x87072)

# list of avaliable fonts
FONT_LIST = [
    'Ariel', 'Times New Roman', 'Courier', "Serif"
]
# dictionary of text weights
FONT_WEIGHT_MAP = {
    'Normal': omr.MUIDrawManager.kWeightNormal,
    'DemiBold': omr.MUIDrawManager.kWeightDemiBold,
    'Bold': omr.MUIDrawManager.kWeightBold,
}


def maya_useNewAPI():
    pass


class controlChaosHUDData(om.MUserData):
    def __init__(self):
        super(controlChaosHUDData, self).__init__(False)


class controlChaosHUDNode(omui.MPxLocatorNode):

    DRAW_DB_CLASSIFICATION = 'drawdb/geometry/controlchaoshud'
    DRAW_REGISTRANT_ID = 'controlChaosHUDNode'

    TEXT_ATTRIBUTES = [
        'top_left_text', 'top_center_text', 'top_right_text',
        'bottom_left_text', 'bottom_center_text', 'bottom_right_text'
    ]
    TEXT_POSITION_NUMBER = 6

    def __init__(self):
        omui.MPxLocatorNode.__init__(self)

    def excludeAsLocator(self):
        return False

    def postConstructor(self):
        this_object = self.thisMObject()
        node = om.MFnDagNode(this_object)

        hidden_attributes = [
            u'localPosition', u'localPositionX', u'localPositionY', u'localPositionZ',
            u'localScale', u'localScaleX', u'localScaleY', u'localScaleZ'
        ]
        for attribute in hidden_attributes:
            attr_object = node.attribute(attribute)
            plug = om.MPlug(this_object, attr_object)
            plug.isLocked = True
            plug.isChannelBox = False
            plug.isKeyable = False

    @classmethod
    def initialize(cls):
        string_attr = om.MFnStringData()
        typed_attr = om.MFnTypedAttribute()
        numeric_attr = om.MFnNumericAttribute()
        enum_attr = om.MFnEnumAttribute()
        compound_fn = om.MFnCompoundAttribute()

        for text_attribute in cls.TEXT_ATTRIBUTES:
            string_data = string_attr.create(text_attribute)
            attr = typed_attr.create(text_attribute, text_attribute, om.MFnData.kString, string_data)
            typed_attr.hidden = True
            cls.addAttribute(attr)

        # top text font
        cls.top_text_font = enum_attr.create('top_text_font', 'top_text_font', 0)
        for index, font_name in enumerate(FONT_LIST):
            enum_attr.addField(font_name, index)

        # add the overall text scale
        cls.overall_text_scale = numeric_attr.create('overall_text_scale', 'overall_text_scale', om.MFnNumericData.kFloat, 1.0)
        numeric_attr.setMin(0.5)
        numeric_attr.setMax(2.0)
        cls.addAttribute(cls.overall_text_scale)

        # offset both text in y
        cls.text_y_offset = numeric_attr.create('text_y_offset', 'text_y_offset', om.MFnNumericData.kInt, 0)
        numeric_attr.setMin(-50)
        numeric_attr.setMax(50)
        cls.addAttribute(cls.text_y_offset)

        # top text controls
        cls.top_text_font_weight = enum_attr.create('top_text_font_weight', 'top_text_font_weight', 0)
        font_weights = list(FONT_WEIGHT_MAP.keys())
        for index, font_weight in enumerate(font_weights):
            enum_attr.addField(font_weight, index)

        # top text colour
        cls.top_text_color = numeric_attr.createColor('top_text_color', 'top_text_color')
        numeric_attr.default = (1.0, 1.0, 1.0)

        # top text alpha
        cls.top_text_alpha = numeric_attr.create(
            'top_text_alpha', 'top_text_alpha', om.MFnNumericData.kFloat, 1.0
        )
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)

        # add scale controller
        cls.top_text_scale = numeric_attr.create(
            'top_text_scale', 'top_text_scale', om.MFnNumericData.kFloat, 1.0
        )
        numeric_attr.setMin(0.2)
        numeric_attr.setMax(5.0)

        cls.top_text_padding = numeric_attr.create('top_text_padding', 'top_text_padding', om.MFnNumericData.kInt, 20)
        numeric_attr.setMin(0)
        numeric_attr.setMax(50)

        # add all top text controls to compound
        cls.top_text_controls = compound_fn.create("Top Text Controls", "top_text_controls")
        compound_fn.addChild(cls.top_text_font)
        compound_fn.addChild(cls.top_text_font_weight)
        compound_fn.addChild(cls.top_text_color)
        compound_fn.addChild(cls.top_text_alpha)
        compound_fn.addChild(cls.top_text_scale)
        compound_fn.addChild(cls.top_text_padding)
        cls.addAttribute(cls.top_text_controls)

        cls.bottom_text_color = numeric_attr.createColor('bottom_text_color', 'bottom_text_color')
        numeric_attr.default = (1.0, 1.0, 1.0)

        # top text font
        cls.bottom_text_font = enum_attr.create('bottom_text_font', 'bottom_text_font', 0)
        for index, font_name in enumerate(FONT_LIST):
            enum_attr.addField(font_name, index)

        cls.bottom_text_font_weight = enum_attr.create('bottom_text_font_weight', 'bottom_text_font_weight', 0)
        font_weights = list(FONT_WEIGHT_MAP.keys())
        for index, font_weight in enumerate(font_weights):
            enum_attr.addField(font_weight, index)

        # add bottom alpha
        cls.bottom_text_alpha = numeric_attr.create(
            'bottom_text_alpha', 'bottom_text_alpha', om.MFnNumericData.kFloat, 1.0
        )
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)

        # add all top text controls to compound
        cls.bottom_text_scale = numeric_attr.create(
            'bottom_text_scale', 'bottom_text_scale', om.MFnNumericData.kFloat, 1.0
        )
        numeric_attr.setMin(0.2)
        numeric_attr.setMax(5.0)

        # add bottom controls
        cls.bottom_text_padding = numeric_attr.create(
            'bottom_text_padding', 'bottom_text_padding', om.MFnNumericData.kInt, 20
        )
        numeric_attr.setMin(0)
        numeric_attr.setMax(50)

        cls.bottom_text_controls = compound_fn.create("Bottom Text Controls", "bottom_text_controls")
        compound_fn.addChild(cls.bottom_text_font)
        compound_fn.addChild(cls.bottom_text_font_weight)
        compound_fn.addChild(cls.bottom_text_color)
        compound_fn.addChild(cls.bottom_text_alpha)
        compound_fn.addChild(cls.bottom_text_scale)
        compound_fn.addChild(cls.bottom_text_padding)
        cls.addAttribute(cls.bottom_text_controls)

        # 1. add focal length parameter
        cls.placeholder1 = numeric_attr.createColor('placeholder1', 'placeholder1')
        numeric_attr.hidden = True

        cls.show_focal_length = numeric_attr.create(
            'show_focal_length', 'show_focal_length', om.MFnNumericData.kBoolean, True
        )

        cls.focal_length_position = numeric_attr.create(
            'focal_length_position', 'focal_length_position', om.MFnNumericData.kInt, 0)
        numeric_attr.setMin(0)
        numeric_attr.setMax(6)

        # add to the compound attribute
        cls.camera_focal_length = compound_fn.create("Camera Focal Length", "camera_focal_length")
        compound_fn.addChild(cls.show_focal_length)
        compound_fn.addChild(cls.focal_length_position)
        compound_fn.addChild(cls.placeholder1)
        cls.addAttribute(cls.camera_focal_length)

        # 2. show camera rotation option
        cls.show_camera_rotations = numeric_attr.create(
            'show_camera_rotations', 'show_camera_rotations', om.MFnNumericData.kBoolean, True
        )

        # add camera rotation options
        cls.camera_rotations_position = numeric_attr.create(
            'camera_rotations_position', 'camera_rotations_position', om.MFnNumericData.kInt, 1)
        numeric_attr.setMin(0)
        numeric_attr.setMax(6)

        # add to the compound attribute
        cls.camera_rotations_grp = compound_fn.create("Camera Rotations", "camera_rotations")
        compound_fn.addChild(cls.show_camera_rotations)
        compound_fn.addChild(cls.camera_rotations_position)
        cls.addAttribute(cls.camera_rotations_grp)

        # show camera height option
        cls.show_camera_height = numeric_attr.create(
            'show_camera_height', 'show_camera_height', om.MFnNumericData.kBoolean, True
        )

        # 3. add camera height options
        cls.camera_height_position = numeric_attr.create(
            'camera_height_position', 'camera_height_position', om.MFnNumericData.kInt, 2)
        numeric_attr.setMin(0)
        numeric_attr.setMax(6)

        cls.camera_height_units = enum_attr.create('camera_height_units', 'camera_height_units', 0)
        enum_attr.addField('Meters', 0)
        enum_attr.addField('Feet', 1)

        cls.ground_geo = typed_attr.create("ground_geo", "ground_geo", om.MFnData.kString)

        # add to the compound attribute
        cls.camera_height_grp = compound_fn.create("Camera Height", "camera_height")
        compound_fn.addChild(cls.show_camera_height)
        compound_fn.addChild(cls.camera_height_position)
        compound_fn.addChild(cls.camera_height_units)
        compound_fn.addChild(cls.ground_geo)
        cls.addAttribute(cls.camera_height_grp)

        # 4. show frame number
        cls.show_frame_number = numeric_attr.create(
            'show_frame_number', 'show_frame_number', om.MFnNumericData.kBoolean, True
        )
        # add frame counter group
        cls.frame_number_position = numeric_attr.create(
            'frame_number_position', 'frame_number_position', om.MFnNumericData.kInt, 3
        )
        numeric_attr.setMin(0)
        numeric_attr.setMax(6)

        cls.frame_padding = numeric_attr.create(
            'frame_padding', 'frame_padding', om.MFnNumericData.kInt, 4
        )
        numeric_attr.setMin(2)
        numeric_attr.setMax(6)

        # need placeholder for it to add the compound group
        cls.placeholder2 = numeric_attr.createColor('placeholder2', 'placeholder2')
        numeric_attr.hidden = True

        # add all to the frame number group
        cls.frame_number_grp = compound_fn.create("Frame Number", "frame_number_grp")
        compound_fn.addChild(cls.show_frame_number)
        compound_fn.addChild(cls.frame_number_position)
        compound_fn.addChild(cls.frame_padding)
        compound_fn.addChild(cls.placeholder2)
        cls.addAttribute(cls.frame_number_grp)

        # 5. add camera speed attribute
        cls.show_camera_speed = numeric_attr.create(
            'show_camera_speed', 'show_camera_speed', om.MFnNumericData.kBoolean, True
        )
        cls.camera_speed_position = numeric_attr.create(
            'camera_speed_position', 'camera_speed_position', om.MFnNumericData.kInt, 4)
        numeric_attr.setMin(0)
        numeric_attr.setMax(6)

        # add to compound group
        cls.camera_speed_grp = compound_fn.create("Camera Speed", "speed_options")
        compound_fn.addChild(cls.show_camera_speed)
        compound_fn.addChild(cls.camera_speed_position)
        cls.addAttribute(cls.camera_speed_grp)

        # 6. distance to actor
        cls.show_distance_to_object = numeric_attr.create(
            'show_distance_to_object', 'show_distance_to_object', om.MFnNumericData.kBoolean, True
        )
        cls.distance_to_actor_position = numeric_attr.create(
            'distance_to_actor_position', 'distance_to_actor_position', om.MFnNumericData.kInt, 5)
        numeric_attr.setMin(0)
        numeric_attr.setMax(6)

        cls.object_name = typed_attr.create("object_name", "object_name", om.MFnData.kString)

        cls.distance_to_actor_grp = compound_fn.create("Distance To Actor", "distance_to_actor")
        compound_fn.addChild(cls.show_distance_to_object)
        compound_fn.addChild(cls.distance_to_actor_position)
        compound_fn.addChild(cls.object_name)
        cls.addAttribute(cls.distance_to_actor_grp)

    @classmethod
    def creator(cls):
        return cls()

    def draw(self, view, path, style, status):
        """Legacy viewport (VP1) draw callback."""
        pass


class controlChaosHUDDrawOverride(omr.MPxDrawOverride):

    def __init__(self, obj):
        super(controlChaosHUDDrawOverride, self).__init__(obj, controlChaosHUDDrawOverride.draw)

    def supportedDrawAPIs(self):
        return (
            omr.MRenderer.kAllDevices
        )

    def isBounded(self, obj_path, camera_path):
        return False

    def boundingBox(self, obj_path, camera_path):
        return om.MBoundingBox()

    def get_frame_string(self, chaos_hud_node, show_frame_number):
        # type: (om.MFnDagNode, bool) -> str
        """
        Get the frame number as a string
        
        Args:
            chaos_hud_node: The node to get the frame plug for
            show_frame_number: Whether to show the frame number

        Returns:
            frame_number_str: The text to show of the frame number
        """
        # work out the frame number as text
        if not show_frame_number:
            return str()
        frame_padding = chaos_hud_node.findPlug('frame_padding', False).asInt()
        current_frame = int(omanim.MAnimControl.currentTime().value)
        frame_number_str = str(current_frame).zfill(frame_padding)
        return frame_number_str

    def get_focal_length_string(self, frame_context, show_focal_length):
        # type: (omr.MFrameContext, bool) -> str
        """
        Get the camera focal length display string

        Args:
            frame_context: The frame context
            show_focal_length: Whether to display the focal length

        Returns:
            focal_length_str: The focal length text
        """
        # work out the frame number as text
        if not show_focal_length:
            return str()
        camera_path = frame_context.getCurrentCameraPath()
        camera = om.MFnCamera(camera_path)
        focal_length_str = "Focal Length: %.2f" % camera.focalLength
        return focal_length_str

    def get_world_position_at_time(self, dep_fn, frame):
        # type: (om.MFnDependencyNode) -> om.MVector
        """
        Get an objects position at a particular frame
        
        Args:
            dep_fn: The dependency node to find
            frame: Frame to get the position

        Returns:
            Current vector position
        """
        # Build an MTime for the desired frame
        time = om.MTime(frame, om.MTime.uiUnit())

        # Use MDGContext to evaluate at a specific time
        ctx = om.MDGContext(time)

        # Pull the worldMatrix attribute value at that time
        world_matrix_plug = dep_fn.findPlug("worldMatrix", False)
        world_matrix_plug = world_matrix_plug.elementByLogicalIndex(0)  # instance 0

        mobj = world_matrix_plug.asMObject(ctx)
        matrix_data = om.MFnMatrixData(mobj)
        matrix = matrix_data.matrix()
        tx = matrix[12]
        ty = matrix[13]
        tz = matrix[14]
        return om.MVector(tx, ty, tz)

    def get_camera_speed_mph(self, frame_context, show_camera_and_object_speed):
        # type: (omr.MFrameContext, bool) -> str
        """
        Returns the speed of a node at a given frame in mph.
        Uses central differencing for accuracy.

        Args:
            frame_context: The frame context
            show_camera_and_object_speed: Whether to display the text

        Returns:
            full_speed_text: The full speed text
        """
        if not show_camera_and_object_speed:
            return str()
        transform_dag = self.get_transform_dag_from_frame_context(frame_context)
        camera_speed = self.get_transform_dag_speed(transform_dag)

        # get camera name
        cam_path = frame_context.getCurrentCameraPath()
        cam_path.pop()  # walk up to transform
        camera_name = om.MFnDagNode(cam_path).name()  # e.g. "persp"
        camera_speed_text = f"{camera_name}:{camera_speed}"
        return camera_speed_text

    def get_transform_dag_speed(self, transform_dag):
        # type: (om.MDagNode) -> str
        """
        From an objects transform get its speed at the current frame
        
        Args:
            transform_dag: The transform dag node

        Returns:
            speed_mph_str: The speed text to display
        """
        dep_fn = om.MFnDependencyNode(transform_dag.node())

        frame = omanim.MAnimControl.currentTime().value

        # get the frames per second as float
        one_second = om.MTime(1.0, om.MTime.kSeconds)
        fps_pre_rounded = one_second.asUnits(om.MTime.uiUnit())
        fps = round(fps_pre_rounded, 3)

        p1 = self.get_world_position_at_time(dep_fn, frame=frame+1)
        p0 = self.get_world_position_at_time(dep_fn, frame=frame-1)

        # Get linear unit as float (units per meter)
        unit = om.MDistance.uiUnit()
        unit_as_meters = om.MDistance(1, unit).asMeters()
        metres_per_unit = round(unit_as_meters, 3)

        # get the complete distance
        distance_m = (p1 - p0).length() * metres_per_unit

        # Central difference: delta spans 2 frames
        speed_mps = (distance_m / 2) * fps       # metres per second
        speed_mph = speed_mps * 2.23694          # 1 m/s = 2.23694 mph
        speed_mph_str = f"{speed_mph:8.3f} mph"
        return speed_mph_str

    def get_camera_translation(self, frame_context):
        # type: (omr.MFrameContext) -> tuple
        """
        Get the cameras current translation for the frame context

        Args:
            frame_context: The frame context

        Returns:
            translation: vector of the current position
        """
        transform_dag = self.get_transform_dag_from_frame_context(frame_context)
        transform_fn = om.MFnTransform(transform_dag)
        translation = transform_fn.translation(om.MSpace.kWorld)
        return translation

    def get_camera_height_to_geo(self, frame_context, ground_geo):
        """
        Fires a ray straight down (-Y) from the camera and returns
        the distance to the first piece of geometry hit.

        Args:
            camera_name (str): Name of the camera transform node.

        Returns:
            float or None: Distance in world units, or None if nothing was hit.
        """
        hit_distance = None
        if not ground_geo:
            return hit_distance
        cam_pos = self.get_camera_translation(frame_context)

        ray_origin    = om.MFloatPoint(cam_pos.x, cam_pos.y, cam_pos.z)
        ray_direction = om.MFloatVector(0, -1, 0)   # straight down

        # Accelerator speeds up repeated intersection tests
        accel = om.MMeshIsectAccelParams()

        # Get a mesh by name
        sel = om.MSelectionList()
        try:
            sel.add(ground_geo)
        except RuntimeError:
            return hit_distance
        dag = sel.getDagPath(0)
        fn_mesh = om.MFnMesh(dag)

        hit = fn_mesh.closestIntersection(
            ray_origin,
            ray_direction,
            om.MSpace.kWorld,
            9999999,        # max distance
            False,          # test both directions?
        )

        if hit is not None:
            hit_point, hit_ray_param, hit_face, hit_tri, hit_bary1, hit_bary2 = hit
            if hit_ray_param > 0:   # must be below the camera
                if hit_distance is None or hit_ray_param < hit_distance:
                    hit_distance = hit_ray_param
        return hit_distance

    def get_camera_height_string(self, frame_context, show_camera_height, camera_height_units_int, ground_geo):
        # type: (omr.MFrameContext, bool, int, str) -> str
        """
        Get the cameras current height in meters or feet

        Args:
            frame_context: The frame context
            show_camera_height: Whether to display the height
            camera_height_units_int: Show it in meters or feet
            ground_geo: The name of the ground geo

        Returns:
            camera_height_str: Camera height text to display
        """
        # work out the frame number as text
        if not show_camera_height:
            return str()
        translationy = self.get_camera_height_to_geo(frame_context, ground_geo)
        if not translationy:
            return "No distance found"
        linear_unit = om.MDistance.uiUnit()

        # Compare against enum and convert to meters
        if linear_unit == om.MDistance.kCentimeters:
            ty = translationy * 100
        elif linear_unit == om.MDistance.kMeters:
            ty = translationy
        elif linear_unit == om.MDistance.kMillimeters:
            ty = translationy * 1000
        else:
            return "unit not found"

        # convert to feet
        if camera_height_units_int == 1:
            height = ty * 3.28084
            camera_height_str = "Height: %.2f ft" % height
        else:
            camera_height_str = "Height: %.2f m" % ty
        return camera_height_str

    def get_transform_dag_from_frame_context(self, frame_context):
        # type: (omr.MFrameContext) -> om.MDagPath
        """
        From the frame context get the camera transform dag

        Args:
            frame_context: The frame context

        Returns:
            transform_dag: The camera as a dag object
        """
        camera_path = frame_context.getCurrentCameraPath()
        camera = om.MFnCamera(camera_path)

        # Get the transform DAG path by popping the shape
        transform_dag = camera.dagPath()
        transform_dag.pop()
        return transform_dag

    def get_camera_rotations(self, frame_context, show_camera_rotations):
        # type: (omr.MFrameContext, bool) -> str
        """
        Get the cameras current rotations as display text

        Args:
            frame_context: The frame context
            show_camera_rotations: Whether to show the rotations

        Returns:
            rotations_text: The rotations display text
        """
        if not show_camera_rotations:
            return str()

        # get the rotations from the dag object
        transform_dag = self.get_transform_dag_from_frame_context(frame_context)
        transform_fn = om.MFnTransform(transform_dag)
        euler = transform_fn.rotation(om.MSpace.kTransform)   # MEulerRotation

        # get them rotations in degrees
        rx = math.degrees(euler.x)
        ry = math.degrees(euler.y)
        rz = math.degrees(euler.z)
        rotations_text = f"rx: %.2f  ry: %.2f  rz: %.2f" % (rx, ry, rz)
        return rotations_text

    def get_distance_to_actor(self, frame_context, show_distance_to_object, object_name):
        # type: (omr.MFrameContext, bool, str) -> str
        """
        Get the distance from the camera to the given object name

        Args:
            frame_context: The frame context
            show_distance_to_object: Whether to show the distance to the object
            object_name: The object to measure the distance to

        Returns:
            distance_to_camera_text: The text to display on the hud
        """
        if not show_distance_to_object:
            return str()
        if not object_name:
            return "No object name given"

        sel = om.MSelectionList()
        try:
            sel.add(object_name)
        except RuntimeError:
            return f"{object_name} not found"

        # get the actors translation
        dag = sel.getDagPath(0)
        transform_fn = om.MFnTransform(dag)
        actor_tr = transform_fn.translation(om.MSpace.kWorld)

        # get the camera translations get the difference
        cam_tr = self.get_camera_translation(frame_context)
        dist = (actor_tr - cam_tr).length()
        distance_to_camera_text = "Distance to %s -- %.2f" % (object_name, dist)
        return distance_to_camera_text

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        data = old_data
        if not isinstance(data, controlChaosHUDData):
            data = controlChaosHUDData()

        chaos_hud_node = om.MFnDagNode(obj_path)
        data.text_fields = []
        for attribute in controlChaosHUDNode.TEXT_ATTRIBUTES:
            data.text_fields.append(chaos_hud_node.findPlug(attribute, False).asString())

        data.top_text_padding = chaos_hud_node.findPlug('top_text_padding', False).asInt()
        data.bottom_text_padding = chaos_hud_node.findPlug('bottom_text_padding', False).asInt()
        data.top_text_scale = chaos_hud_node.findPlug('top_text_scale', False).asFloat()
        data.bottom_text_scale = chaos_hud_node.findPlug('bottom_text_scale', False).asFloat()

        # Get top text font
        top_text_font_plug = chaos_hud_node.findPlug('top_text_font', False)
        enum_fn = om.MFnEnumAttribute(top_text_font_plug.attribute())
        data.top_text_font = enum_fn.fieldName(top_text_font_plug.asInt())

        # Get bottom text font
        bottom_text_font_plug = chaos_hud_node.findPlug('bottom_text_font', False)
        enum_fn = om.MFnEnumAttribute(bottom_text_font_plug.attribute())
        data.bottom_text_font = enum_fn.fieldName(bottom_text_font_plug.asInt())

        # general scale
        data.overall_text_scale = chaos_hud_node.findPlug('overall_text_scale', False).asFloat()
        data.text_y_offset = chaos_hud_node.findPlug('text_y_offset', False).asFloat()

        # get the text colours
        top_text_color_r = chaos_hud_node.findPlug('top_text_colorR', False).asFloat()
        top_text_color_g = chaos_hud_node.findPlug('top_text_colorG', False).asFloat()
        top_text_color_b = chaos_hud_node.findPlug('top_text_colorB', False).asFloat()
        top_text_color_a = chaos_hud_node.findPlug('top_text_alpha', False).asFloat()
        data.top_text_color = om.MColor(
            (top_text_color_r, top_text_color_g, top_text_color_b, top_text_color_a)
        )

        # get top text font weight
        top_text_font_weight_plug = chaos_hud_node.findPlug('top_text_font_weight', False)
        top_text_font_weight_attr = om.MFnEnumAttribute(top_text_font_weight_plug.attribute())
        data.top_text_font_weight = FONT_WEIGHT_MAP.get(
            top_text_font_weight_attr.fieldName(top_text_font_weight_plug.asShort())
        )

        # create the lower text colour
        bottom_text_color_r = chaos_hud_node.findPlug('bottom_text_colorR', False).asFloat()
        bottom_text_color_g = chaos_hud_node.findPlug('bottom_text_colorG', False).asFloat()
        bottom_text_color_b = chaos_hud_node.findPlug('bottom_text_colorB', False).asFloat()
        bottom_text_color_a = chaos_hud_node.findPlug('bottom_text_alpha', False).asFloat()
        data.bottom_text_color = om.MColor(
            (bottom_text_color_r, bottom_text_color_g, bottom_text_color_b, bottom_text_color_a)
        )

        # bottom text font weight
        bottom_text_font_weight_plug = chaos_hud_node.findPlug('bottom_text_font_weight', False)
        bottom_text_font_weight_attr = om.MFnEnumAttribute(bottom_text_font_weight_plug.attribute())
        data.bottom_text_font_weight = FONT_WEIGHT_MAP.get(
            bottom_text_font_weight_attr.fieldName(bottom_text_font_weight_plug.asShort())
        )

        # set the frame number text position
        frame_number_position = chaos_hud_node.findPlug('frame_number_position', False).asInt()
        show_frame_number = chaos_hud_node.findPlug('show_frame_number', False).asBool()
        if 0 <= frame_number_position < controlChaosHUDNode.TEXT_POSITION_NUMBER:
            frame_string = self.get_frame_string(chaos_hud_node, show_frame_number)
            data.text_fields[frame_number_position] = frame_string

        # get the camera focal length to display
        focal_length_position = chaos_hud_node.findPlug('focal_length_position', False).asInt()
        show_focal_length = chaos_hud_node.findPlug('show_focal_length', False).asBool()
        if 0 <= focal_length_position < controlChaosHUDNode.TEXT_POSITION_NUMBER:
            focal_length_string = self.get_focal_length_string(frame_context, show_focal_length)
            data.text_fields[focal_length_position] = focal_length_string

        # get the camera height and display it
        camera_height_position = chaos_hud_node.findPlug('camera_height_position', False).asInt()
        show_camera_height = chaos_hud_node.findPlug('show_camera_height', False).asBool()
        if 0 <= camera_height_position < controlChaosHUDNode.TEXT_POSITION_NUMBER:
            # Get camera height
            camera_height_units_int = chaos_hud_node.findPlug('camera_height_units', False).asInt()
            ground_geo = chaos_hud_node.findPlug('ground_geo', False).asString()
            camera_height_string = self.get_camera_height_string(
                frame_context, show_camera_height, camera_height_units_int, ground_geo)
            data.text_fields[camera_height_position] = camera_height_string

        # get the camera rotations
        camera_rotations_position = chaos_hud_node.findPlug('camera_rotations_position', False).asInt()
        show_camera_rotations = chaos_hud_node.findPlug('show_camera_rotations', False).asBool()
        if 0 <= camera_rotations_position < controlChaosHUDNode.TEXT_POSITION_NUMBER:
            camera_rotations = self.get_camera_rotations(frame_context, show_camera_rotations)
            data.text_fields[camera_rotations_position] = camera_rotations

        # work out the camera speed
        camera_speed_position = chaos_hud_node.findPlug('camera_speed_position', False).asInt()
        show_camera_speed = chaos_hud_node.findPlug('show_camera_speed', False).asBool()

        if 0 <= camera_speed_position < controlChaosHUDNode.TEXT_POSITION_NUMBER:
            camera_speed = self.get_camera_speed_mph(frame_context, show_camera_speed)
            data.text_fields[camera_speed_position] = camera_speed

        # get the distance to an actor
        distance_to_actor_position = chaos_hud_node.findPlug('distance_to_actor_position', False).asInt()
        object_name = chaos_hud_node.findPlug('object_name', False).asString()

        show_distance_to_object = chaos_hud_node.findPlug('show_distance_to_object', False).asBool()
        if 0 <= distance_to_actor_position < controlChaosHUDNode.TEXT_POSITION_NUMBER:
            distance_to_actor = self.get_distance_to_actor(frame_context, show_distance_to_object, object_name)
            data.text_fields[distance_to_actor_position] = distance_to_actor
        return data

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        if not isinstance(data, controlChaosHUDData):
            return
        camera_path = frame_context.getCurrentCameraPath()
        camera = om.MFnCamera(camera_path)
        camera_aspect_ratio = camera.aspectRatio()
        device_aspect_ratio = cmds.getAttr('defaultResolution.deviceAspectRatio')

        viewport_x, viewport_y, viewport_width, viewport_height = frame_context.getViewportDimensions()
        viewport_aspect_ratio = viewport_width / float(viewport_height)

        scale = 1.0
        if camera.filmFit == om.MFnCamera.kHorizontalFilmFit:
            mask_width = viewport_width / camera.overscan
            mask_height = mask_width / device_aspect_ratio

        elif camera.filmFit == om.MFnCamera.kVerticalFilmFit:
            mask_height = viewport_height / camera.overscan
            mask_width = mask_height * device_aspect_ratio

        elif camera.filmFit in (om.MFnCamera.kFillFilmFit, om.MFnCamera.kOverscanFilmFit):
            if camera_aspect_ratio > device_aspect_ratio:
                scale = device_aspect_ratio / camera_aspect_ratio

            elif viewport_aspect_ratio < camera_aspect_ratio:
                scale = min(camera_aspect_ratio, device_aspect_ratio) / viewport_aspect_ratio
            else:
                pass

            if camera.filmFit == om.MFnCamera.kFillFilmFit:
                mask_width = viewport_width / camera.overscan * scale
                mask_height = mask_width / device_aspect_ratio
            else:
                mask_height = viewport_height / camera.overscan / scale
                mask_width = mask_height * device_aspect_ratio
        else:
            om.MGlobal.displayError('[controlChaosHUD] Unknown Film Fit Value')
            return
#

        mask_x = 0.5 * (viewport_width - mask_width)
        mask_y_top = 0.5 * (viewport_height + mask_height + data.text_y_offset)
        mask_y_bottom = 0.5 * (viewport_height - mask_height + (data.text_y_offset * -1))

        #if not data.crop_enabled:
        border_height = int(0.1 * mask_height * data.overall_text_scale)

        if border_height <= 0:
            om.MGlobal.displayWarning(
                "controlChaosHUD's height pixel <= 0 ({0}), current crop preset not "
                "suit for current scene render size.".format(border_height)
            )
            return
        background_size = (int(mask_width), border_height)

        # draw mask
        draw_manager.beginDrawable()

        draw_manager.setFontName(data.top_text_font)
        draw_manager.setFontWeight(data.top_text_font_weight)
        draw_manager.setColor(data.top_text_color)
        draw_manager.setFontSize(int(border_height * 0.25 * data.top_text_scale))

        self.draw_text(
            draw_manager, om.MPoint(mask_x+data.top_text_padding, mask_y_top-border_height),
            data.text_fields[0], omr.MUIDrawManager.kLeft, background_size
        )
        self.draw_text(
            draw_manager, om.MPoint(viewport_width*0.5, mask_y_top-border_height),
            data.text_fields[1], omr.MUIDrawManager.kCenter, background_size
        )
        self.draw_text(
            draw_manager, om.MPoint(mask_x+mask_width-data.top_text_padding, mask_y_top-border_height),
            data.text_fields[2], omr.MUIDrawManager.kRight, background_size
        )

        draw_manager.setFontName(data.bottom_text_font)
        draw_manager.setFontWeight(data.bottom_text_font_weight)
        draw_manager.setColor(data.bottom_text_color)
        draw_manager.setFontSize(int(border_height * 0.25 * data.bottom_text_scale))

        self.draw_text(
            draw_manager, om.MPoint(mask_x+data.bottom_text_padding, mask_y_bottom),
            data.text_fields[3], omr.MUIDrawManager.kLeft, background_size
        )
        self.draw_text(
            draw_manager, om.MPoint(viewport_width*0.5, mask_y_bottom),
            data.text_fields[4], omr.MUIDrawManager.kCenter, background_size
        )
        self.draw_text(
            draw_manager, om.MPoint(mask_x+mask_width-data.bottom_text_padding, mask_y_bottom),
            data.text_fields[5], omr.MUIDrawManager.kRight, background_size
        )

        draw_manager.endDrawable()

    @staticmethod
    def draw_text(draw_manager, position, text, alignment, background_size):
        if not len(text):
            return
        draw_manager.text2d(
            position, text, alignment=alignment,
            backgroundSize=background_size,
            backgroundColor=om.MColor((1.0, 0.0, 0.0, 0.0)),
            dynamic=False
        )

    @staticmethod
    def creator(obj):
        return controlChaosHUDDrawOverride(obj)

    @staticmethod
    def draw(context, data):
        return


def initializePlugin(obj):
    plugin = om.MFnPlugin(obj, 'astips', PLUGIN_VERSION, 'Any')
    try:
        plugin.registerNode(
            NODE_NAME, NODE_ID, controlChaosHUDNode.creator, controlChaosHUDNode.initialize,
            om.MPxNode.kLocatorNode, controlChaosHUDNode.DRAW_DB_CLASSIFICATION
        )
    except SyntaxError:
        sys.stderr.write('Loading Error')
        raise Exception('Failed to register controlChaosHUD Node.')

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(
            controlChaosHUDNode.DRAW_DB_CLASSIFICATION,
            controlChaosHUDNode.DRAW_REGISTRANT_ID,
            controlChaosHUDDrawOverride.creator
        )
    except SyntaxError:
        sys.stderr.write('Loading Error')
        raise Exception('Failed to register controlChaosHUDDrawOverride.')


def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(
            controlChaosHUDNode.DRAW_DB_CLASSIFICATION,
            controlChaosHUDNode.DRAW_REGISTRANT_ID
        )
    except SyntaxError:
        sys.stderr.write('Removing Error')
        raise Exception('Failed to de-register controlChaosHUDDrawOverride.')

    try:
        plugin.deregisterNode(NODE_ID)
    except SyntaxError:
        sys.stderr.write('Removing Error')
        raise Exception('Failed to de-register controlChaosHUD Node.')

