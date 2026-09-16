""" Camera utilities function in Houdini """

import hou


def constraint_camera(source_camera_path):
    # type: (str) -> hou.Node
    """
    Create a new camera at world space

    Args:
        source_camera_path: The path of the original camera

    Returns:
        target_camera: The newly created camera
    """
    target_camera = hou.node("/obj").createNode("cam", "temp_camera")
    extract_to_axis = {
        "extractTranslates": ["tx", "ty", "tz"],
        "extractRotates": ["rx", "ry", "rz"]
    }

    translate_parms = []
    for extract, axis_list in extract_to_axis.items():
        for index, axis in enumerate(axis_list):
            expr = f'hou.node("{source_camera_path}").worldTransform().{extract}()[{index}]'
            target_camera.parm(axis).setExpression(expr, hou.exprLanguage.Python)
            translate_parms.append(axis)

    source_camera = hou.node(source_camera_path)
    for parm in source_camera.allParms():
        parm_name = parm.name()

        # if the parameter doesn't exist on the target
        # camera or if it is a transform skip
        target_parm = target_camera.parm(parm_name)
        if not target_parm or parm_name in translate_parms:
            continue

        # if specific named parameters exist skip
        if "xform1" in parm.path() or "pathobjpath" in parm.path():
            continue

        # link the parameters
        target_parm.setExpression(f'ch("{parm.path()}")')

    return target_camera
