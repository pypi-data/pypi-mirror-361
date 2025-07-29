# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Custom log levels for MFD modules."""

"""
TEST_PASS log level should be used in test cases to provide information about test result.
TEST_FAIL log level should be used in test cases to provide information about test result.
TEST_STEP log level should be used in test cases to provide information on high level steps being performed.
TEST_INFO log level should be used in test cases to provide additional information between step and debug.
TEST_DEBUG log level should be used in test cases for debug information about steps performed.
BL_STEP log level should be used in Business Logic to provide information on high level steps being performed.
BL_INFO log level should be used in Business Logic to provide additional information between step and debug.
BL_DEBUG log level should be used in Business Logic for debug information for steps performed.
MFD_STEP log level should be used in MFDs to provide information on high level steps being performed.
MFD_INFO log level should be used in MFDs to provide additional information between step and debug.
MFD_DEBUG log level should be used in MFDs for debug information about steps performed and is preferred to MODULE_DEBUG.
MODULE_DEBUG log level should be used when any activity during debugging the module is worth logging.
CMD log level should be used only for executed command line (ex. from mfd-connect execute_command method).
OUT log level should be used only for logging output from executed command line (ex. from mfd-connect execute_command
method).
"""
# Test result levels
TEST_PASS = 29
TEST_FAIL = 28

# Step Levels
TEST_STEP = 27
BL_STEP = 26
MFD_STEP = 25

# Info Levels
TEST_INFO = 23
BL_INFO = 22
MFD_INFO = 21

# Debug Levels
TEST_DEBUG = 16
BL_DEBUG = 15
MFD_DEBUG = 14
MODULE_DEBUG = 13
CMD = 12
OUT = 11
