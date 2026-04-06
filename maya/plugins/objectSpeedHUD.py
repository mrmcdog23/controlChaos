""" Speed hud node to measure the objects speed information """
import sys
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.api.OpenMayaRender as omr
import maya.api.OpenMayaAnim as omanim


# plugin information
PLUGIN_VERSION = '1.0.0'
NODE_NAME = 'objectSpeedHUD'
NODE_ID = om.MTypeId(0x87073)

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

SPEED_UNITS = [
    "Meters Per Second",
    "Kilometers Per Hour",
    "Miles Per Hour",
    "Feet Per Second",
    "Knots Per Hour"
]

NUMBER_OF_OBJECTS = 5


def maya_useNewAPI():
    pass


class objectSpeedHUDData(om.MUserData):
    def __init__(self):
        super(objectSpeedHUDData, self).__init__(False)


class objectSpeedHUDNode(omui.MPxLocatorNode):

    DRAW_DB_CLASSIFICATION = 'drawdb/geometry/objectSpeedHUD'
    DRAW_REGISTRANT_ID = 'objectSpeedHUDNode'

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
        typed_attr = om.MFnTypedAttribute()
        numeric_attr = om.MFnNumericAttribute()
        enum_attr = om.MFnEnumAttribute()
        compound_fn = om.MFnCompoundAttribute()

        # text font to use
        cls.text_font = enum_attr.create('text_font', 'text_font', 0)
        for index, font_name in enumerate(FONT_LIST):
            enum_attr.addField(font_name, index)

        # the text font size attribute
        cls.font_size = numeric_attr.create('font_size', 'font_size', om.MFnNumericData.kInt, 12)
        numeric_attr.setMin(1)
        numeric_attr.setMax(40)

        # text font weight
        cls.font_weight = enum_attr.create('font_weight', 'font_weight', 2)
        font_weights = list(FONT_WEIGHT_MAP.keys())
        for index, font_weight in enumerate(font_weights):
            enum_attr.addField(font_weight, index)

        # unit type to measure the speed
        cls.speed_unit = enum_attr.create('speed_unit', 'speed_unit', 0)
        for index, speed_unit_name in enumerate(SPEED_UNITS):
            enum_attr.addField(speed_unit_name, index)

        cls.addAttribute(cls.font_size)
        cls.addAttribute(cls.text_font)
        cls.addAttribute(cls.font_weight)
        cls.addAttribute(cls.speed_unit)

        # 6. distance to actor
        for index in range(NUMBER_OF_OBJECTS):
            num = str(index + 1)
            cls.show_object_speed = numeric_attr.create(
                f'show_object_speed{num}', f'show_object_speed{num}', om.MFnNumericData.kBoolean, True
            )

            # text display colour
            cls.speed_text_colour = numeric_attr.createColor(f'speed_text_colour{num}', f'speed_text_colour{num}')
            numeric_attr.default = (1.0, 1.0, 1.0)

            # offset both text in y
            cls.text_x_offset = numeric_attr.create(f'text_x_offset{num}', f'text_x_offset{num}', om.MFnNumericData.kInt, 0)
            numeric_attr.setMin(-50)
            numeric_attr.setMax(50)

            # offset both text in y
            cls.text_y_offset = numeric_attr.create(f'text_y_offset{num}', f'text_y_offset{num}', om.MFnNumericData.kInt, 0)
            numeric_attr.setMin(-50)
            numeric_attr.setMax(50)

            # name of the object
            cls.object_name = typed_attr.create(f"object_name{num}", f"object_name{num}", om.MFnData.kString)

            cls.speed_object_grp = compound_fn.create(f"Object Speed {num}", f"speed_object_grp{num}")
            compound_fn.addChild(cls.show_object_speed)
            compound_fn.addChild(cls.speed_text_colour)
            compound_fn.addChild(cls.text_x_offset)
            compound_fn.addChild(cls.text_y_offset)
            compound_fn.addChild(cls.object_name)
            cls.addAttribute(cls.speed_object_grp)

    @classmethod
    def creator(cls):
        return cls()

    def draw(self, view, path, style, status):
        """Legacy viewport (VP1) draw callback."""
        pass


class objectSpeedHUDDrawOverride(omr.MPxDrawOverride):

    def __init__(self, obj):
        super(objectSpeedHUDDrawOverride, self).__init__(obj, objectSpeedHUDDrawOverride.draw)

    def supportedDrawAPIs(self):
        return (
            omr.MRenderer.kAllDevices
        )

    def isBounded(self, obj_path, camera_path):
        return False

    def boundingBox(self, obj_path, camera_path):
        return om.MBoundingBox()

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

    def get_object_speed(self, object_name_speed, speed_unit):
        # type: (om.MDagNode, str) -> str
        """
        From an objects name get its speed at the current frame

        Args:
            object_name_speed: The transform dag node
            speed_unit: The unit to measure the speed in

        Returns:
            speed_str: The speed text to display
        """
        sel = om.MSelectionList()
        try:
            sel.add(object_name_speed)
        except RuntimeError:
            return f"{object_name_speed} not found"

        dag_path = sel.getDagPath(0)
        dep_fn = om.MFnDependencyNode(dag_path.node())

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
        if speed_unit == "Meters Per Second":     # 1 m/s = 2.23694 mph
            speed_str = f"{speed_mps:8.3f} m"

        elif speed_unit == "Kilometers Per Hour":
            speed_mph = speed_mps * 3.6         # 1 m/s = 2.23694 mph
            speed_str = f"{speed_mph:8.3f} kph"

        elif speed_unit == "Miles Per Hour":
            speed_mph = speed_mps * 2.23694          # 1 m/s = 2.23694 mph
            speed_str = f"{speed_mph:8.3f} mph"

        elif speed_unit == "Feet Per Second":
            speed_yph = speed_mps * 3.28084
            speed_str = f"{speed_yph:8.3f} ftps"

        elif speed_unit == "Knots Per Hour":
            speed_knots = speed_mps * 1.94384
            speed_str = f"{speed_knots:8.3f} ktsph"
        return speed_str

    def get_screen_pos(self, object_name, text_x_offset, text_y_offset, frame_context):
        # type: (str, int, int, omr.MFrameContext) -> om.MPoint
        """
        From the information given work out the
        position of the text on screen

        Args:
            object_name: Object to find the text for
            text_x_offset: The offset of the text in X
            text_y_offset: The offset of the text in Y
            frame_context: The frame context

        Returns:
            screen_pos: Text position on screen
        """
        sel = om.MSelectionList()
        try:
            sel.add(object_name)
        except RuntimeError:
            return

        # get the actors translation
        obj_path = sel.getDagPath(0)

        # --- what to show ---------------------------------------------------
        # --- world-space pivot of this node ---------------------------------
        inclusive_matrix = obj_path.inclusiveMatrix()
        world_pos = om.MPoint(0, 0, 0) * inclusive_matrix   # pivot in world

        # --- project world position → NDC (normalized device coordinates) ---
        # frame_context gives us the current camera's view-projection matrix
        # MFloatMatrix path: viewProjection = projection × view
        view_mat = frame_context.getMatrix(
            omr.MFrameContext.kViewMtx)
        proj_mat = frame_context.getMatrix(
            omr.MFrameContext.kProjectionMtx)

        vp_mat   = view_mat * proj_mat          # model→clip space

        # transform world point through view-projection
        pt_clip = om.MPoint(world_pos) * vp_mat
        # perspective divide → NDC  (-1..1)
        if pt_clip.w != 0.0:
            ndc_x = pt_clip.x / pt_clip.w
            ndc_y = pt_clip.y / pt_clip.w
        else:
            ndc_x, ndc_y = 0.0, 0.0

        # --- NDC → viewport pixels ------------------------------------------
        vp_x, vp_y, vp_w, vp_h = frame_context.getViewportDimensions()
        # NDC  (-1,1) → (0,1) → pixel
        px_original = vp_x + (ndc_x * 0.5 + 0.5) * vp_w
        px = text_x_offset + px_original

        # Maya's DrawManager y=0 is BOTTOM; NDC y=+1 is TOP → flip
        py_offset = vp_y + (1.0 - (ndc_y * 0.5 + 0.5)) * vp_h
        py = vp_h - py_offset + text_y_offset
        # store as an MPoint (z ignored by text2d)
        screen_pos = om.MPoint(px, py)
        return screen_pos

    def get_colour_attribute(self, speed_hud_node, colour_name):
        # type: (om.MFnDagNode, str) -> om.MColor
        """
        Get the colour attribute and create an MColor

        Args:
            speed_hud_node: Node with the attribute
            colour_name: Name of the colour attribute

        Returns:
            text_color: Final colour of the text
        """
        text_color_r = speed_hud_node.findPlug(f'{colour_name}R', False).asFloat()
        text_color_g = speed_hud_node.findPlug(f'{colour_name}G', False).asFloat()
        text_color_b = speed_hud_node.findPlug(f'{colour_name}B', False).asFloat()
        text_color = om.MColor((text_color_r, text_color_g, text_color_b, 1.0))
        return text_color

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        data = old_data
        if not isinstance(data, objectSpeedHUDData):
            data = objectSpeedHUDData()

        # build the text fields
        data.text_fields = [i for i in range(NUMBER_OF_OBJECTS)]

        # get the speed node
        speed_hud_node = om.MFnDagNode(obj_path)
        
        # text scale
        data.font_size = speed_hud_node.findPlug('font_size', False).asInt()
        
        # Get top text font
        text_font_plug = speed_hud_node.findPlug('text_font', False)
        enum_fn = om.MFnEnumAttribute(text_font_plug.attribute())
        data.text_font = enum_fn.fieldName(text_font_plug.asInt())

        # get text font weight
        font_weight_plug = speed_hud_node.findPlug('font_weight', False)
        font_weight_attr = om.MFnEnumAttribute(font_weight_plug.attribute())
        data.font_weight = FONT_WEIGHT_MAP.get(
            font_weight_attr.fieldName(font_weight_plug.asShort())
        )

        # get speed unit
        speed_unit_plug = speed_hud_node.findPlug('speed_unit', False)
        enum_fn = om.MFnEnumAttribute(speed_unit_plug.attribute())
        speed_unit = enum_fn.fieldName(speed_unit_plug.asInt())

        # loop through all plugs and get the data
        for index in range(NUMBER_OF_OBJECTS):
            num = str(index + 1)
            object_name = speed_hud_node.findPlug(f'object_name{num}', False).asString()
            show_object_speed = speed_hud_node.findPlug(f'show_object_speed{num}', False).asBool()
            text_x_offset = speed_hud_node.findPlug(f'text_x_offset{num}', False).asFloat()
            text_y_offset = speed_hud_node.findPlug(f'text_y_offset{num}', False).asFloat()

            # get the position, speed and colour
            screen_pos = self.get_screen_pos(object_name, text_x_offset, text_y_offset, frame_context)
            object_speed = self.get_object_speed(object_name, speed_unit)
            speed_text_colour = self.get_colour_attribute(speed_hud_node, f"speed_text_colour{num}")
            data.text_fields[index] = [screen_pos, object_speed, speed_text_colour, show_object_speed]
        return data

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        if not isinstance(data, objectSpeedHUDData):
            return

        # set the font size and weight
        draw_manager.beginDrawable()
        draw_manager.setFontName(data.text_font)
        draw_manager.setFontWeight(data.font_weight)
        draw_manager.setFontSize(data.font_size)

        # show information
        for index in range(NUMBER_OF_OBJECTS):
            position, object_speed, speed_text_colour, show_object_speed = data.text_fields[index]
            draw_manager.setColor(speed_text_colour)

            # draw that plugs text
            self.draw_text(
                draw_manager, position,
                object_speed, omr.MUIDrawManager.kLeft, show_object_speed
            )
        draw_manager.endDrawable()

    @staticmethod
    def draw_text(draw_manager, position, text, alignment, show_text):
        # type: (omui.MUIDrawManager, om.MPoint, int, bool) -> None
        """
        Draw the text on the screen

        Args:
            draw_manager:
            position: Where on screen to put the text
            text: The information to display
            alignment: To have the text left or right
            show_text: Whether to skip the text completely
        """
        if not show_text or not text or not position:
            return
        draw_manager.text2d(
            position, text, alignment=alignment,
            backgroundColor=om.MColor((1.0, 0.0, 0.0, 0.0)),
            dynamic=False
        )

    @staticmethod
    def creator(obj):
        return objectSpeedHUDDrawOverride(obj)

    @staticmethod
    def draw(context, data):
        return


def initializePlugin(obj):
    plugin = om.MFnPlugin(obj, 'astips', PLUGIN_VERSION, 'Any')
    try:
        plugin.registerNode(
            NODE_NAME, NODE_ID, objectSpeedHUDNode.creator, objectSpeedHUDNode.initialize,
            om.MPxNode.kLocatorNode, objectSpeedHUDNode.DRAW_DB_CLASSIFICATION
        )
    except SyntaxError:
        sys.stderr.write('Loading Error')
        raise Exception('Failed to register objectSpeedHUD Node.')

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(
            objectSpeedHUDNode.DRAW_DB_CLASSIFICATION,
            objectSpeedHUDNode.DRAW_REGISTRANT_ID,
            objectSpeedHUDDrawOverride.creator
        )
    except SyntaxError:
        sys.stderr.write('Loading Error')
        raise Exception('Failed to register objectSpeedHUDDrawOverride.')


def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(
            objectSpeedHUDNode.DRAW_DB_CLASSIFICATION,
            objectSpeedHUDNode.DRAW_REGISTRANT_ID
        )
    except SyntaxError:
        sys.stderr.write('Removing Error')
        raise Exception('Failed to de-register objectSpeedHUDDrawOverride.')

    try:
        plugin.deregisterNode(NODE_ID)
    except SyntaxError:
        sys.stderr.write('Removing Error')
        raise Exception('Failed to de-register objectSpeedHUD Node.')

