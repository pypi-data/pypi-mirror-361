# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for custom log level class."""

import logging
from enum import auto, Enum

from . import log_levels


class LevelGroup(Enum):
    """Names of log levels' groups."""

    BL = auto()
    MFD = auto()
    TEST = auto()


def add_logging_level(level_name: str, level_value: int) -> None:
    """
    Add a new logging level to the `logging` module.

    :param level_name: Name visible in log in console itself.
    :param level_value: value of the level.

    Example:
    -------
    >>> from mfd_common_libs import log_levels
    >>> add_logging_level("CMD", log_levels.CMD)
    >>> logger = logging.getLogger(__name__)
    >>> logging.basicConfig(level=log_levels.CMD)
    >>> logger.log(level=log_levels.CMD, msg="cmd message")
    """
    # ignore if logging name is already declared
    if not hasattr(logging, level_name):
        logging.addLevelName(level_value, level_name)
        setattr(logging, level_name, level_value)


def add_logging_group(level_group: LevelGroup) -> None:
    """
    Add all log levels related to the given group to the logging module.

    Can be used instead of addition of levels one by one.

    Example:
    -------
        old way:
            >>> from mfd_common_libs import add_logging_level, log_levels
            >>> add_logging_level("TEST_FAIL", log_levels.TEST_FAIL)
            >>> add_logging_level("TEST_PASS", log_levels.TEST_PASS)
            >>> add_logging_level("TEST_STEP", log_levels.TEST_STEP)
        new way:
            >>> from mfd_common_libs import add_logging_group, LevelGroup
            >>> add_logging_group(LevelGroup.TEST)

    :param level_group: Name of log level group
    """
    known_log_levels = [lvl for lvl in dir(log_levels) if not lvl.startswith("_") and level_group.name in lvl]
    if level_group is LevelGroup.MFD:
        known_log_levels.append("MODULE_DEBUG")  # Used as MFD_DEBUG, should be also considered as MFD level

    for lvl in known_log_levels:
        add_logging_level(lvl, getattr(log_levels, lvl))
