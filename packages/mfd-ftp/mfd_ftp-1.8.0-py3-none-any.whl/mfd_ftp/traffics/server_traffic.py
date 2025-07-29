# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""FTP server traffic."""

import logging
from ipaddress import IPv4Address, IPv6Address
from typing import Union, TYPE_CHECKING, Optional

from mfd_common_libs import log_levels, add_logging_level
from mfd_ftp import ftp_server
from mfd_ftp.traffics.base import FTPTraffic

if TYPE_CHECKING:
    from mfd_connect.process import RemoteProcess
    from mfd_connect import Connection


logger = logging.getLogger(__name__)
add_logging_level("MODULE_DEBUG", log_levels.MODULE_DEBUG)


class FTPServerTraffic(FTPTraffic):
    """Class for FTP server traffic."""

    _process: "RemoteProcess"

    def __init__(
        self,
        connection: "Connection",
        ip: Union[IPv4Address, IPv6Address],
        port: int,
        directory: str,
        username: str,
        password: str,
        python_executable: Optional[str] = None,
        permissions: Optional[str] = None,
    ) -> None:
        """FTP server traffic.

        :param connection: FTP Connection
        :param ip: Address of the FTP server.
        :param port: Number of a port on which server is running.
        :param directory: Path to directory which server should share.
        :param username: Username for the server to login.
        :param password: Password for the user.
        :param python_executable: Executable python
        :param permissions: User permissions, indicating which operations are allowed.
        :return: None
        """
        self._connection = connection
        self.ip = ip
        self.port = port
        self.directory = directory
        self.username = username
        self.password = password
        self.permissions = permissions
        self.python_executable = python_executable

    def start(self) -> None:
        """
        Start FTP server traffic.

        :return: None
        """
        self._process = ftp_server.start_remote_server_as_process(
            connection=self._connection,
            ip=self.ip,
            port=self.port,
            directory=self.directory,
            username=self.username,
            password=self.password,
            python_executable=self.python_executable,
            permissions=self.permissions,
        )

    def run(self, duration: int) -> None:
        """
        Run FTP server traffic.

        :param duration: duration is not supported for server
        :return: None
        """
        self.start()
