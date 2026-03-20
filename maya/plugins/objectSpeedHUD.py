""" Control chaos hud node for camera information """
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
        string_attr = om.MFnStringData()
        typed_attr = om.MFnTypedAttribute()
        numeric_attr = om.MFnNumericAttribute()
        enum_attr = om.MFnEnumAttribute()
        compound_fn = om.MFnCompoundAttribute()

        # top text font
        cls.text_font = enum_attr.create('text_font', 'text_font', 0)
        for index, font_name in enumerate(FONT_LIST):
            enum_attr.addField(font_name, index)

        # add the overall text scale
        cls.font_size = numeric_attr.create('font_size', 'font_size', om.MFnNumericData.kInt, 12)
        numeric_attr.setMin(1)
        numeric_attr.setMax(40)
        cls.addAttribute(cls.font_size)

        # top text controls
        cls.font_weight = enum_attr.create('font_weight', 'font_weight', 2)
        font_weights = list(FONT_WEIGHT_MAP.keys())
        for index, font_weight in enumerate(font_weights):
            enum_attr.addField(font_weight, index)

        cls.addAttribute(cls.text_font)
        cls.addAttribute(cls.font_weight)

        # 6. distance to actor
        cls.show_object_speed1 = numeric_attr.create(
            'show_object_speed1', 'show_object_speed1', om.MFnNumericData.kBoolean, True
        )

        cls.speed_text_colour1 = numeric_attr.createColor('speed_text_colour1', 'speed_text_colour1')
        numeric_attr.default = (1.0, 1.0, 1.0)

        # offset both text in y
        cls.text_x_offset1 = numeric_attr.create('text_x_offset1', 'text_x_offset1', om.MFnNumericData.kInt, 0)
        numeric_attr.setMin(-50)
        numeric_attr.setMax(50)

        # offset both text in y
        cls.text_y_offset1 = numeric_attr.create('text_y_offset1', 'text_y_offset1', om.MFnNumericData.kInt, 0)
        numeric_attr.setMin(-50)
        numeric_attr.setMax(50)

        cls.object_name1 = typed_attr.create("object_name1", "object_name1", om.MFnData.kString)

        cls.speed_object_grp1 = compound_fn.create("Object Speed 1", "speed_object_grp1")
        compound_fn.addChild(cls.show_object_speed1)
        compound_fn.addChild(cls.speed_text_colour1)
        compound_fn.addChild(cls.text_x_offset1)
        compound_fn.addChild(cls.text_y_offset1)
        compound_fn.addChild(cls.object_name1)
        cls.addAttribute(cls.speed_object_grp1)

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

    def get_object_speed(self, object_name_speed):
        # type: (om.MDagNode) -> str
        """
        From an objects transform get its speed at the current frame
        
        Args:
            transform_dag: The transform dag node

        Returns:
            speed_mph_str: The speed text to display
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
        speed_mph = speed_mps * 2.23694          # 1 m/s = 2.23694 mph
        speed_mph_str = f"{speed_mph:8.3f} mph"
        return speed_mph_str

    def get_screen_pos(self, object_name, text_x_offset, text_y_offset, frame_context):
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
        top_text_color_r = speed_hud_node.findPlug(f'{colour_name}R', False).asFloat()
        top_text_color_g = speed_hud_node.findPlug(f'{colour_name}G', False).asFloat()
        top_text_color_b = speed_hud_node.findPlug(f'{colour_name}B', False).asFloat()
        top_text_color = om.MColor(
            (top_text_color_r, top_text_color_g, top_text_color_b, 1.0)
        )
        return top_text_color

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        data = old_data
        if not isinstance(data, objectSpeedHUDData):
            data = objectSpeedHUDData()
        
        data.text_fields = [0, 1, 2, 3, 4, 5]
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

        object_name1 = speed_hud_node.findPlug('object_name1', False).asString()
        show_object_speed1 = speed_hud_node.findPlug('show_object_speed1', False).asBool()
        text_x_offset1 = speed_hud_node.findPlug('text_x_offset1', False).asFloat()
        text_y_offset1 = speed_hud_node.findPlug('text_y_offset1', False).asFloat()

        screen_pos1 = self.get_screen_pos(object_name1, text_x_offset1, text_y_offset1, frame_context)
        object_speed1 = self.get_object_speed(object_name1)
        speed_text_colour1 = self.get_colour_attribute(speed_hud_node, "speed_text_colour1")
        data.text_fields[0] = [screen_pos1, object_speed1, speed_text_colour1, show_object_speed1]

        return data

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        if not isinstance(data, objectSpeedHUDData):
            return

        draw_manager.beginDrawable()
        draw_manager.setFontName(data.text_font)
        draw_manager.setFontWeight(data.font_weight)
        draw_manager.setFontSize(data.font_size)

        # show information
        mpoint, object_speed, speed_text_colour1, show_object_speed1 = data.text_fields[0]
        draw_manager.setColor(speed_text_colour1)

        self.draw_text(
            draw_manager, mpoint,
            object_speed, omr.MUIDrawManager.kLeft, show_object_speed1
        )
        draw_manager.endDrawable()

    @staticmethod
    def draw_text(draw_manager, position, text, alignment, show_text):
        if not show_text:
            return
        if not position:
            return
        if not len(text):
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

