# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT

"""Module for timeout counter class."""

from time import time


class TimeoutCounter:
    """
    Timeout counter object.

    bool(obj) will return False before timer runs out and True after.

    Example:
    -------
    >>> from time import sleep
    >>>
    >>> timeout = TimeoutCounter(10)
    >>> bool(timeout)
    False
    >>> sleep(10)
    >>> bool(timeout)
    True

    Can be used to conveniently wait for timeout to happen, e.g.:
    >>> from time import sleep
    >>>
    >>> timeout = TimeoutCounter(10)
    >>> while not timeout:
    ...     if <condition>:
    ...         return
    ...     sleep(1)
    ... else:
    ...     raise TimeoutError("Time's up!")
    """

    def __init__(self, timeout: float, *, first_check_start: bool = True) -> None:
        """
        Init of TimeoutCounter.

        :param timeout: Time, after which bool(obj) will become True
        :param first_check_start: If True - start counting from the first bool(obj) attempt,
                                  otherwise counting is started at object creation.
        """
        super().__init__()
        self._timeout = timeout
        self._time_is_up = False

        if not first_check_start:
            self._start_time = time()
            self._end_time = self._start_time + self._timeout
        else:
            self._start_time = None

    def __bool__(self) -> bool:
        if self._time_is_up:
            return True

        if self._start_time is None:
            self._start_time = time()
            self._end_time = self._start_time + self._timeout
            return False

        if self._end_time < time():
            self._time_is_up = True
            return True

        return False
