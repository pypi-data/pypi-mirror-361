# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for LibibverbsTool class."""

import logging
from abc import ABC
from typing import Optional

from mfd_base_tool import ToolTemplate
from mfd_typing import OSName
from mfd_common_libs import os_supported

from .exceptions import LibibverbsToolNotAvailable

logger = logging.getLogger(__name__)


class LibibverbsTool(ToolTemplate, ABC):
    """
    Abstract class for all libibverbs tools.

    Usage example:
    >>> class IBVDevices(LibibverbsTool):
    >>> ...
    """

    __init__ = os_supported(OSName.LINUX, OSName.FREEBSD)(ToolTemplate.__init__)

    def _get_tool_exec_factory(self) -> str:
        """Get correct tool name."""
        return self.tool_executable_name

    def _get_tool_exec(self, tool_path_dir: Optional[str]) -> str:
        """
        Get path to tool binary.

        :param tool_path_dir: path to dir where binary of tool is stored
        :return: path to tool binary

        :raises LibibverbsToolNotAvailable when tool cannot be found in $PATH
        """
        if tool_path_dir is not None:
            return str(self._connection.path(tool_path_dir, self.tool_executable_name))
        else:
            # libibverbs tools are applicable only on Linux/BSD OSes
            which_cmd = f"which {self.tool_executable_name}"
            return self._connection.execute_command(
                command=which_cmd, custom_exception=LibibverbsToolNotAvailable
            ).stdout.strip()

    def check_if_available(self) -> None:
        """
        Check if tool is available.

        :raises LibibverbsToolNotAvailable when tool not available.
        """
        # libibverbs tools are applicable only on Linux/BSD OSes
        check_cmd = f"test -x {self._tool_exec}"
        self._connection.execute_command(command=check_cmd, custom_exception=LibibverbsToolNotAvailable)

    def get_version(self) -> str:
        """
        Get version of Libibverbs tools.

        :return: Version of tool
        """
        logger.debug("Tool does not have version.")
        return "N/A"
