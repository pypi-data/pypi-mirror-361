# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for libibverbs utils exceptions."""

import subprocess

from mfd_base_tool.exceptions import ToolNotAvailable


class IBVDevicesException(subprocess.CalledProcessError):
    """Raised when ibv_devices command would fail."""


class LibibverbsToolNotAvailable(ToolNotAvailable, FileNotFoundError):
    """Raised when libibverbs tool not found."""


class IBVDevinfoException(subprocess.CalledProcessError):
    """Raised when ibv_devinfo command would fail."""


class ParsingError(Exception):
    """Raised if a data can't be retrieved based on an output of a command."""
