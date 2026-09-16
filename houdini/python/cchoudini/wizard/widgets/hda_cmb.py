""" Combo boxes for hda suffixes """
import cccore.base_ui as base_ui


SUFFIXES = ["Ldev", "Model", "LightRig"]


class HDAWidget(base_ui.WidgetBase):
    def __init__(self):
        """
        The Ftrack combo boxes for loading assets and versions
        """
        super(HDAWidget, self).__init__()
        self.cmb_suffix.addItems(SUFFIXES)
