""" Customize the logger to set the level and format """
import logging
from typing import Optional


def cc_logger(level=None):
    # type: (Optional[logging.Logger.level]) -> logging.Logger
    """
    Create the control chaos logger with formatted text

    Args:
        level: The logging level to use

    Returns:
        logger: Created logger to use
    """
    logger = logging.getLogger()
    for handler in logger.handlers[:]:  # make a copy of the list
        logger.removeHandler(handler)

    if not level:
        level = logging.INFO
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # prevent logging from bubbling up to maya's logger
    logger.propagate = False
    return logger

