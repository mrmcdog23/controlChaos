""" Export FBX cameras to Unreal """
import json
import maya.cmds as cmds
import ccmaya.utils.maya_utils as maya_utils
import cccore.base_ui as base_ui
import cccore.utils.cc_logging as cc_logging
from ccgeneral.widgets.line_browser import LineBrowser
from CCPySide import QtWidgets, QtCore


class ExportAnimationCurves(base_ui.WindowBase):
    title = "Export Animation Curves"

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.logger = cc_logging.cc_logger()

        # run setup functions
        self.create_layout()
        self.connect_signals()

    def create_layout(self):
        """
        Create the layout for the ui
        """
        self.browse_output_wdg = LineBrowser(
            self, "save", "Select Animation File", "", "Animation File")
        self.lyt_browse.addWidget(self.browse_output_wdg)

    def connect_signals(self):
        """
        Connect the signal to the widgets
        """
        self.btn_export_anim.clicked.connect(self.export_anim)

    def get_all_anim_curves(self):
        """
        All animCurve nodes (TL, TA, TU, TT, UL, UA, UU, UT), skipping referenced ones.
        """
        curves = cmds.ls(type="animCurve") or []
        return [c for c in curves if not cmds.referenceQuery(c, isNodeReferenced=True)]

    def export_anim(self):
        """
        Export animation to the given json file
        """
        file_path = self.browse_output_wdg.file_path
        if not file_path.endswith(".json"):
            file_path += ".json"

        # run the export animation data
        data = {}
        for crv in self.get_all_anim_curves():
            times = cmds.keyframe(crv, query=True, timeChange=True) or []
            values = cmds.keyframe(crv, query=True, valueChange=True) or []
            in_type = cmds.keyTangent(crv, query=True, inTangentType=True) or []
            out_type = cmds.keyTangent(crv, query=True, outTangentType=True) or []
            in_angle = cmds.keyTangent(crv, query=True, inAngle=True) or []
            out_angle = cmds.keyTangent(crv, query=True, outAngle=True) or []
            in_wt = cmds.keyTangent(crv, query=True, inWeight=True) or []
            out_wt = cmds.keyTangent(crv, query=True, outWeight=True) or []

            # Which attribute(s) does this curve drive?
            targets = cmds.listConnections(crv + ".output", plugs=True, source=False,
                                           destination=True) or []

            data[crv] = {
                "targets": targets,
                "preInfinity": cmds.setInfinity(crv, query=True, preInfinite=True),
                "postInfinity": cmds.setInfinity(crv, query=True, postInfinite=True),
                "keys": [
                    {
                        "time": t, "value": v,
                        "inTangentType": it, "outTangentType": ot,
                        "inAngle": ia, "outAngle": oa,
                        "inWeight": iw, "outWeight": ow,
                    }
                    for t, v, it, ot, ia, oa, iw, ow in zip(
                        times, values, in_type, out_type,
                        in_angle, out_angle, in_wt, out_wt)
                ],
            }

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        self.logger.info(f"Exported {len(data)} curves to {file_path}")

        # display the completed message
        QtWidgets.QMessageBox.information(
            self, "Exported Animation", "Exported Animation Data", QtWidgets.QMessageBox.Ok
        )


def main():
    """ Launch the maya export animation curves """
    maya_utils.launch_maya_win(ExportAnimationCurves)