""" Select options to run the tile render """
import cccore.base_ui as base_ui


class TileRenderingWidget(base_ui.WidgetBase):
    def __init__(self):
        """
        The Ftrack combo boxes for loading assets and versions
        """
        super(TileRenderingWidget, self).__init__()
        self.connect_signals()

    def connect_signals(self):
        """
        Connect the slider to the spinbox
        """
        self.sld_tiles_x.valueChanged.connect(self.set_tiles_x)
        self.sld_tiles_y.valueChanged.connect(self.set_tiles_y)

    def set_tiles_x(self, value):
        # type: (int) -> None
        """
        Set the number of tile in X from the slider
        """
        self.sb_tiles_x.setValue(value / 10)

    def set_tiles_y(self, value):
        # type: (int) -> None
        """
        Set the number of tile in Y from the slider
        """
        self.sb_tiles_y.setValue(value / 10)

    @property
    def tile_y(self):
        # type: () -> int
        """
        The number of tiles in Y
        """
        return self.sb_tiles_y.value()

    @property
    def tile_x(self):
        # type: () -> int
        """
        The number of tiles in X
        """
        return self.sb_tiles_x.value()

    @property
    def do_tile_rendering(self):
        # type: () -> bool
        """
        Whether to do tile rendering
        """
        return self.grp_tile_rendering.isChecked()
