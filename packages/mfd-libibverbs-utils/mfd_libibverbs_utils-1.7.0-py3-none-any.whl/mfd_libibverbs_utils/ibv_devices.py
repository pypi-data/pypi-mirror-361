# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for IBVDevices class."""

import logging
import re
from dataclasses import dataclass
from typing import Optional, List, Iterator

from .exceptions import IBVDevicesException
from .libibverbs_tool import LibibverbsTool

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IBDevice:
    """Dataclass for 'ibv_devices' output."""

    device: str
    node_guid: str


class IBVDevices(LibibverbsTool):
    """
    Class for handling 'ibv_devices' command tool line to get information about RDMA devices on system.

    Usage example:
    >>> ibv_dev = IBVDevices(connection=mfd_connect.RPyCConnection('192.0.8.2'))
    >>> ibv_dev.get_list()
    [IBDevice(device='mlx5_0', node_guid='506b4b0300ccf69e'),
    IBDevice(device='cxgb4_0', node_guid='0007434742000000')]
    """

    tool_executable_name = "ibv_devices"

    def _get_parsed_ibv_devices(self, output: str) -> Iterator[Optional[IBDevice]]:
        """
        Parse output from 'ibv_devices' and convert it to IBDevice objects.

        :param output: Output from cmd 'ibv_devices'.
        :return: Iterator over IBDevice objects.
        """
        ibv_dev_regex = r"\s+(?P<device>\w+)\s+" r"(?P<node_guid>\w+)"
        header_lines = ("device", "------")
        for dev in re.finditer(pattern=ibv_dev_regex, string=output, flags=re.MULTILINE):
            if dev.group("device").startswith(header_lines):
                # Ignore header lines
                continue
            yield IBDevice(**dev.groupdict())

    def get_list(self) -> List[Optional[IBDevice]]:
        """
        List RDMA devices available for use from userspace.

        :return: List of IBDevice objects.

        :raises IBVDevicesException when executed cmd fails.
        """
        cmd = self._tool_exec
        completed_process = self._connection.execute_command(cmd, custom_exception=IBVDevicesException)

        return list(dev for dev in self._get_parsed_ibv_devices(completed_process.stdout))
