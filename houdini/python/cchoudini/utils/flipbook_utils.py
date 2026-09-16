""" Utilities relating specifically to flipbook """
import toolutils


def set_flipbook_output():
    """
    Set the flipbook settings to ensure its publishable
    """
    scene = toolutils.sceneViewer()
    settings = scene.flipbookSettings()
    settings.useResolution(True)
    settings.resolution((1920, 1080))
    settings.output("$APPDATA/flipbook/$HIPNAME/$HIPNAME.$F4.jpg")
