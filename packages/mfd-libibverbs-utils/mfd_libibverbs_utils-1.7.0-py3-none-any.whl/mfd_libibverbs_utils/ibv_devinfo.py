# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for IBVDevinfo class."""

import dataclasses
import logging
import re
from dataclasses import dataclass
from typing import Optional, List, Iterator, Union

from .exceptions import IBVDevinfoException, ParsingError
from .ibv_devices import IBDevice
from .libibverbs_tool import LibibverbsTool

logger = logging.getLogger(__name__)


@dataclass
class IBDevPhysicalPort:
    """Dataclass for definition of physical port from 'ibv_devices' output."""

    number: int
    state: str
    max_mtu: int
    active_mtu: int
    sm_lid: int
    port_lid: int
    port_lmc: str
    link_layer: str

    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                setattr(self, field.name, field.type(value))


@dataclass
class IBDeviceInfo:
    """Dataclass for 'ibv_devinfo' output."""

    name: str
    transport: str
    fw_ver: str
    node_guid: str
    sys_image_guid: str
    vendor_id: str
    vendor_part_id: str
    hw_ver: str
    board_id: str
    phys_port_cnt: int
    physical_ports: List[IBDevPhysicalPort] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.phys_port_cnt, int):
            self.phys_port_cnt = int(self.phys_port_cnt)


class IBVDevinfo(LibibverbsTool):
    """
    Class for handling 'ibv_devinfo' command tool line to get information about RDMA devices on system.

    Usage example:
    >>> ibv_dev = IBVDevinfo(connection=mfd_connect.RPyCConnection('192.0.8.2'))
    >>> ibv_dev.get_info()
    [IBDeviceInfo(name='cxgb4_0', transport='iWARP (1)', fw_ver='1.23.4.0', node_guid='0007:4347:4200:0000',
                         sys_image_guid='0007:4347:4200:0000', vendor_id='0x1425', vendor_part_id='25608',
                         hw_ver='0x0', board_id='1425.6408', phys_port_cnt=2, physical_ports=[
                    IBDevPhysicalPort(number=1, state='PORT_DOWN (1)', max_mtu=4096, active_mtu=1024, sm_lid=0,
                                      port_lid=0, port_lmc='0x00', link_layer='Ethernet')])]
    """

    tool_executable_name = "ibv_devinfo"

    def _get_parsed_ibv_devinfo(self, output: str) -> Iterator[IBDeviceInfo]:
        """
        Parse output from 'ibv_devinfo' and convert it to IBDeviceInfo objects.

        :param output: Output from cmd 'ibv_devinfo'.
        :return: Iterator over IBDeviceInfo objects.
        """
        phys_port_regex = (
            r"port:\s+(?P<number>\d+)\n\s+"
            r"state:\s+(?P<state>\S+\s\S+)\n\s+"
            r"max_mtu:\s+(?P<max_mtu>\d+)\s\S+\n\s+"
            r"active_mtu:\s+(?P<active_mtu>\d+)\s\S+\n\s+"
            r"sm_lid:\s+(?P<sm_lid>\d+)\n\s+"
            r"port_lid:\s+(?P<port_lid>\d+)\n\s+"
            r"port_lmc:\s+(?P<port_lmc>\w+)\n\s+"
            r"link_layer:\s+(?P<link_layer>\w+)\n\s+"
        )
        ib_devinfo_regex = (
            r"\s(?P<name>\w+)\n\s+"
            r"transport:\s+(?P<transport>\S+\s\S+)\n\s+"
            r"fw_ver:\s+(?P<fw_ver>\S+)\n\s+"
            r"node_guid:\s+(?P<node_guid>\S+)\n\s+"
            r"sys_image_guid:\s+(?P<sys_image_guid>\S+)\n\s+"
            r"vendor_id:\s+(?P<vendor_id>\w+)\n\s+"
            r"vendor_part_id:\s+(?P<vendor_part_id>\d+)\n\s+"
            r"hw_ver:\s+(?P<hw_ver>\w+)\n\s+"
            r"board_id:\s+(?P<board_id>\S+)\n\s+"
            r"phys_port_cnt:\s+(?P<phys_port_cnt>\d+)\n\s+"
            r"(?P<ports_data>(\n|.)*)"
        )
        devices_raw = output.split("hca_id:")
        for dev_raw in devices_raw:
            try:
                if not dev_raw:
                    # Ignore empty items
                    continue
                dev_match = re.match(ib_devinfo_regex, dev_raw)
                if not dev_match:
                    raise ParsingError("IB device info data was parsed incorrectly!")
                dev_dict = dev_match.groupdict()
                port_data = dev_dict.pop("ports_data")
                dev = IBDeviceInfo(**dev_dict)
                for port in re.finditer(pattern=phys_port_regex, string=port_data, flags=re.MULTILINE):
                    port_dict = port.groupdict()
                    port_obj = IBDevPhysicalPort(**port_dict)
                    dev.physical_ports.append(port_obj)
                yield dev
            except KeyError as err:
                raise ParsingError from err

    def get_info(
        self, *, ib_device: Optional[Union[str, IBDevice]] = None, ib_port: Optional[int] = None
    ) -> List[Optional[IBDeviceInfo]]:
        """
        Get detailed info about RDMA devices available for use from userspace.

        :param ib_device: name of the IB device or object of IBDevice (from IBVDevices) for which info will be queried.
        :param ib_port: number of port for which info will be queried.
        :return: List of IBDeviceInfo objects.

        :raises IBVDevinfoException when executed cmd fails.
        """
        if isinstance(ib_device, IBDevice):
            ib_device = ib_device.device

        cmd = self._tool_exec
        if ib_device:
            cmd += f" -d {ib_device}"
        if ib_port:
            cmd += f" -i {ib_port}"

        completed_process = self._connection.execute_command(
            cmd, expected_return_codes={0, 255}, custom_exception=IBVDevinfoException
        )
        if completed_process.return_code == 255:
            logger.debug("No IB devices found.")
            return []

        return list(dev for dev in self._get_parsed_ibv_devinfo(completed_process.stdout))
