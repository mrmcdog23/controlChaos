""" Import animation data """
import json
from collections import Counter
import maya.cmds as cmds
import ccmaya.utils.maya_utils as maya_utils
import cccore.base_ui as base_ui
import cccore.utils.cc_logging as cc_logging
from ccgeneral.widgets.line_browser import LineBrowser
from CCPySide import QtWidgets, QtCore


class ImportAnimationData(base_ui.WindowBase):
    title = "Import Animation Data"

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.logger = cc_logging.cc_logger()
        self.create_layout()
        self.connect_signals()

    def create_layout(self):
        """
        Create the layout for the ui
        """
        self.browse_output_wdg = LineBrowser(
            self, "file", "Select Animation File", "", "Animation File")
        self.lyt_browse.addWidget(self.browse_output_wdg)

    def connect_signals(self):
        """
        Connect the signal to the widgets
        """
        self.btn_import_anim.clicked.connect(self.import_anim)
        self.browse_output_wdg.line_edit.textChanged.connect(self.populate_data)

    def get_namespaces(self):
        """
        Return {namespace: number_of_driven_attributes} for an exported anim JSON.
        """
        file_path = self.browse_output_wdg.file_path
        with open(file_path, "r") as f:
            data = json.load(f)

        namespaces_set = set()
        for info in data.values():
            for plug in info.get("targets", []):
                node_path = plug.split(".")[0]  # drop attribute
                for part in node_path.split("|"):  # each DAG path element
                    if ":" in part:
                        namespace = part.rsplit(":", 1)[0]
                        namespaces_set.add(namespace)
        return list(namespaces_set)

    def populate_data(self):
        namespaces_list = self.get_namespaces()
        for namespace in namespaces_list:
            item = QtWidgets.QListWidgetItem(namespace)
            self.lw_namespaces.addItem(item)

    # ------------------------------------------------------------------ helpers
    def _remap_plug(self, plug, namespace=None, strip_existing_ns=True, node_map=None):
        """
        'ns:ctrl|ns:child.translateX' style plug names -> the name on the target rig.

        node_map : optional dict {old_node_short_name: new_node_name} for rigs whose
                   control names differ between source and target.
        """
        node, _, attr = plug.partition(".")
        short = node.split("|")[-1]  # drop DAG path
        if strip_existing_ns:
            short = short.split(":")[-1]  # drop old namespace

        if node_map:
            short = node_map.get(short, node_map.get(node.split("|")[-1], short))

        if namespace:
            ns = namespace.strip(":")
            short = "{}:{}".format(ns, short)

        return "{}.{}".format(short, attr)

    def _plug_is_keyable(self, plug):
        if not cmds.objExists(plug):
            return False, "does not exist"
        if cmds.getAttr(plug, lock=True):
            return False, "locked"
        return True, ""

    def import_curves_from_json(self, path, namespace=None, strip_existing_ns=True,
                                node_map=None, time_offset=0.0, replace_existing=True,
                                apply_tangents=True):
        """
        Recreate animation from a JSON file onto objects in the current scene.

        namespace        : target rig namespace, e.g. "rigA" (None = no namespace)
        strip_existing_ns: remove whatever namespace the source file used
        node_map         : {"old_ctrl": "new_ctrl"} renames for differing rigs
        time_offset      : shift all keys (frames), e.g. 100 to start at frame 100
        replace_existing : delete existing keys on the attribute first
        apply_tangents   : restore tangent types/angles/weights (set False for speed)
        """
        with open(path, "r") as f:
            data = json.load(f)

        applied, skipped = 0, []

        cmds.undoInfo(openChunk=True, chunkName="importAnimCurves")
        try:
            for curve_name, info in data.items():
                keys = info.get("keys", [])
                if not keys:
                    continue

                for src_plug in info.get("targets", []):
                    plug = self._remap_plug(src_plug, namespace, strip_existing_ns, node_map)

                    ok, reason = self._plug_is_keyable(plug)
                    if not ok:
                        skipped.append((plug, reason))
                        continue

                    # An attribute driven by something other than an anim curve
                    # (constraint, expression, etc.) can't take keys.
                    src_conn = cmds.listConnections(plug, source=True, destination=False,
                                                    plugs=False) or []
                    non_anim = [n for n in src_conn
                                if not cmds.objectType(n).startswith("animCurve")]
                    if non_anim:
                        skipped.append((plug, "driven by " + non_anim[0]))
                        continue

                    if replace_existing:
                        cmds.cutKey(plug, clear=True)

                    # Pass 1: keys
                    for k in keys:
                        cmds.setKeyframe(plug, time=k["time"] + time_offset, value=k["value"])

                    # Pass 2: tangents
                    if apply_tangents:
                        cmds.keyTangent(plug, edit=True, weightedTangents=True)
                        for k in keys:
                            t = k["time"] + time_offset
                            it, ot = k["inTangentType"], k["outTangentType"]

                            # Types first (angles are only honoured for "fixed")
                            cmds.keyTangent(plug, edit=True, time=(t, t),
                                            inTangentType=it, outTangentType=ot)

                            kwargs = {}
                            if it == "fixed":
                                kwargs.update(inAngle=k["inAngle"], inWeight=k["inWeight"])
                            if ot == "fixed":
                                kwargs.update(outAngle=k["outAngle"], outWeight=k["outWeight"])
                            if kwargs:
                                cmds.keyTangent(plug, edit=True, time=(t, t),
                                                lock=False, **kwargs)

                    # Pre/post infinity
                    crv = cmds.listConnections(plug, source=True, destination=False) or []
                    if crv:
                        if info.get("preInfinity"):
                            cmds.setInfinity(crv[0], preInfinite=info["preInfinity"])
                        if info.get("postInfinity"):
                            cmds.setInfinity(crv[0], postInfinite=info["postInfinity"])

                    applied += 1
        finally:
            cmds.undoInfo(closeChunk=True)

        print("Applied animation to {} attributes.".format(applied))
        if skipped:
            print("Skipped {} attributes:".format(len(skipped)))
            for plug, reason in skipped:
                print("  {}  ({})".format(plug, reason))
        return applied, skipped

    def import_anim(self):
        namespaces_list = self.get_namespaces()
        for namespace in namespaces_list:
            self.import_curves_from_json(
                self.browse_output_wdg.file_path, namespace=namespace)


def main():
    """ Launch the maya import animation DATA """
    maya_utils.launch_maya_win(ImportAnimationData)