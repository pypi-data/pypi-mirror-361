# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""FTP client traffic."""

import logging
from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Union, TYPE_CHECKING

from mfd_common_libs import log_levels, add_logging_level
from mfd_ftp.client import ftp_client
from mfd_ftp.traffics.base import FTPTraffic


if TYPE_CHECKING:
    from mfd_connect.process import RemoteProcess
    from mfd_connect import Connection

logger = logging.getLogger(__name__)
add_logging_level("MODULE_DEBUG", log_levels.MODULE_DEBUG)


class FTPClientTraffic(FTPTraffic):
    """Class for FTP client traffic."""

    _process: "RemoteProcess"

    def __init__(
        self,
        connection: "Connection",
        ip: Union[IPv4Address, IPv6Address],
        port: int,
        username: str,
        password: str,
        task: str,
        source: str,
        destination: str,
        python_executable: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """FTP client traffic.

        :param connection: FTP Connection
        :param ip: Address of the FTP server.
        :param port: Number of a port on which server is running.
        :param username: Username for the server to login.
        :param password: Password for the user.
        :param task: Task for the client, can either be 'send' or 'receive'.
        :param source: File to either receive or send.
        :param destination: Destination for the received or sent file.
        :param python_executable: Executable python
        :param timeout: Timeout in seconds for operations, like connection attempt, or transfer.
        :return: None
        """
        self._connection = connection
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.task = task
        self.source = source
        self.destination = destination
        self.python_executable = python_executable
        self.timeout = timeout

    def start(self) -> None:
        """
        Start FTP client traffic.

        :return: None
        """
        self._process = ftp_client.start_remote_client_as_process(
            connection=self._connection,
            ip=self.ip,
            port=self.port,
            username=self.username,
            password=self.password,
            task=self.task,
            source=self.source,
            destination=self.destination,
            python_executable=self.python_executable,
            timeout=self.timeout,
        )
