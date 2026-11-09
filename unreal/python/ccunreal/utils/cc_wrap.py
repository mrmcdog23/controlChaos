""" Wrapper for custom python code """
import unreal as ue
from typing import Optional


def notification(message, icon, duration=2, success=True):
    # type: (str, str, Optional[int], Optional[boo]) -> None
    """
    Notify the artist once something has successfully been run

    Args:
        message: The text to display on the message
        icon: name of the icon to display
        duration: Time in seconds for the message to show
        success: True if the command is a success
    """
    ue.CCBlueprintLibrary.popup_message(message, icon, duration=duration, success=success)