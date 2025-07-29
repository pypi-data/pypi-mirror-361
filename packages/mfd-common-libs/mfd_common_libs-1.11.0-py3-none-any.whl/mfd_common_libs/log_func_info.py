# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for func info decorator."""

from functools import wraps
from logging import Logger
from typing import Any, Callable
from mfd_common_libs import log_levels, add_logging_level

add_logging_level("MODULE_DEBUG", log_levels.MODULE_DEBUG)


def log_func_info(logger: Logger) -> Any:
    """
    Log details of executed function (name, args, kwargs).

    :param logger: Logger object to use
    :return: Decorated function
    """

    def decorate(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(*args, **kwargs) -> Any:
            message_list = [f"Calling func: {function.__name__}"]
            if args or kwargs:
                message_list.append("with")
                if args:
                    message_list.append(f"arguments: {list(args)}")
                if kwargs:
                    message_list.append(f"keyword arguments: {kwargs}")
            logger.log(level=log_levels.MODULE_DEBUG, msg=" ".join(message_list))
            return function(*args, **kwargs)

        return wrapper

    return decorate
