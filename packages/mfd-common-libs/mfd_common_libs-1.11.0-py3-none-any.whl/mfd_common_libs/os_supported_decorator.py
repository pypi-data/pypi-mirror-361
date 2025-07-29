# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for os supported decorator."""

import logging
import typing
from functools import wraps
from typing import Any, Callable

from mfd_common_libs.exceptions import UnexpectedOSException, OSSupportedDecoratorError
from mfd_common_libs.log_func_info import add_logging_level
from mfd_common_libs.log_levels import MODULE_DEBUG

if typing.TYPE_CHECKING:
    from mfd_typing import OSName

logger = logging.getLogger(__name__)
add_logging_level(level_name="MODULE_DEBUG", level_value=MODULE_DEBUG)


def os_supported(*expected_os: "OSName") -> Any:
    """
    Check supported OS via connection from function kwargs.

    mfd-connect module is required.

    :param expected_os: Expected OS/OSes
    :return: Decorated function
    :raises OSSupportedDecoratorError: if not found necessary 'connection'
    :raises UnexpectedOSException: if OS is unexpected
    """
    def decorate(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(*args, **kwargs) -> Any:
            try:
                from mfd_connect import Connection
            except ImportError:
                logger.log(level=MODULE_DEBUG, msg=f"mfd-connect module is not installed. Skipping OS verification.")
                return function(*args, **kwargs)
            for kwarg_name, kwarg_value in kwargs.items():
                if isinstance(kwarg_value, Connection):
                    connection = kwargs[kwarg_name]
                    read_os = connection.get_os_name()
                    if read_os not in expected_os:
                        raise UnexpectedOSException(f"Found unexpected OS: {read_os.value}")
                    break
            else:
                raise OSSupportedDecoratorError("Connection object not found in keyword arguments of wrapped function!")
            return function(*args, **kwargs)

        return wrapper

    return decorate
