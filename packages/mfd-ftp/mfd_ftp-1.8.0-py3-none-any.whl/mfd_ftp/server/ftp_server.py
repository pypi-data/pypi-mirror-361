# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Checking args and starting server as process."""

import logging
import subprocess
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from ipaddress import ip_address, IPv4Address, IPv6Address
from pathlib import Path
from typing import Any, Dict, Union, TYPE_CHECKING, Optional

from mfd_common_libs import log_levels, add_logging_level, TimeoutCounter
from mfd_connect import RPyCConnection, LocalConnection
from mfd_ftp.util.exceptions import FTPModuleExceptions
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer


if TYPE_CHECKING:
    from mfd_connect.process import RemoteProcess
    from mfd_connect import Connection


logger = logging.getLogger("mfd_ftp_server")
add_logging_level(level_value=log_levels.MODULE_DEBUG, level_name="MODULE_DEBUG")
logger.setLevel(log_levels.MODULE_DEBUG)


def _parse_args() -> Dict[str, Any]:
    """
    Parse commandline arguments.

    :return: Config for the tool execution.
    """
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "--ip",
        metavar="<ip>",
        type=ip_address,
        default=ip_address("127.0.0.1"),
        help="IP address for the server to work on, if not given localhost address is passed.",
    )
    parser.add_argument(
        "--port",
        metavar="<port>",
        type=int,
        default=21,
        help="Network port for the server, if not given default port %(default)s is passed.",
    )
    parser.add_argument(
        "--directory",
        metavar="<directory>",
        required=True,
        type=Path,
        help="Directory for the server to serve files from.",
    )
    parser.add_argument(
        "--username", metavar="<username>", required=True, type=str, help="Username for the user to login with."
    )
    parser.add_argument("--password", metavar="<password>", required=True, type=str, help="Password for the user.")
    parser.add_argument(
        "--permissions",
        metavar="<permissions>",
        type=str,
        default="elradfmwMT",
        help="Permissions for the server. if not given all permissions are enabled\n"
        "example: 'elradfmw' each character represent different permission, full list:\n"
        "Read permissions:\n"
        "- 'e' = change directory (CWD command)\n"
        "- 'l' = list files (LIST, NLST, STAT, MLSD, MLST, SIZE, MDTM commands)\n"
        "- 'r' = retrieve file from the server (RETR command)\n"
        "Write permissions:\n"
        "- 'a' = append data to an existing file (APPE command)\n"
        "- 'd' = delete file or directory (DELE, RMD commands)\n"
        "- 'f' = rename file or directory (RNFR, RNTO commands)\n"
        "- 'm' = create directory (MKD command)\n"
        "- 'w' = store a file to the server (STOR, STOU commands)\n"
        "- 'M' = change file mode (SITE CHMOD command)\n"
        "- 'T' = update file last modified time (MFMT command)\n",
    )
    return vars(parser.parse_args())


def _get_server(
    ip: Union[IPv4Address, IPv6Address], port: int, username: str, password: str, directory: Path, permissions: str
) -> ThreadedFTPServer:
    """
    Create and return FTP server, with desired directory, user and permissions.

    :param ip: IP address for the server to work on.
    :param port: Port for the server to listen.
    :param username: Username on which client should login.
    :param password: Password for a user to login.
    :param directory: Path to directory which server should share.
    :param permissions: User permissions, indicating which operations are allowed.
    :return Object of the FTP server.
    """
    authorizer = DummyAuthorizer()
    authorizer.add_user(username, password, str(directory), permissions)
    handler = FTPHandler
    handler.authorizer = authorizer

    return ThreadedFTPServer((str(ip), port), handler)


@staticmethod
def _validate_arguments_correctness(process: "RemoteProcess") -> None:
    """
    Check correctness of passed arguments after start of process.

    :param process: FTPProcess
    :raises: FTPModuleException if passed incorrect args
    """
    timeout = TimeoutCounter(1)
    while not timeout:
        if process.running:
            continue
        if process.log_path is not None:
            output = process.log_path.read_text()
        else:
            output = process.stdout_text
        if "invalid option" in output:
            raise FTPModuleExceptions("Passed unsupported option as args.")
        else:
            logger.log(level=log_levels.MODULE_DEBUG, msg=output)
            raise FTPModuleExceptions(f"Server/client is not running: {output}")


def start_server_as_process(
    ip: ip_address,
    port: int,
    directory: Union[Path, str],
    username: str,
    password: str,
    permissions: Optional[str] = None,
) -> subprocess.Popen:
    """
    Start server as process.

    :param ip: IP address for the server to work on.
    :param port: Port for the server to listen.
    :param username: Username on which client should login.
    :param password: Password for a user to login.
    :param directory: Path to directory which server should share.
    :param permissions: User permissions, indicating which operations are allowed.
    :return Object of server process.
    """
    command = [
        str(sys.executable),
        "-m",
        "mfd_ftp.server",
        "--ip",
        str(ip),
        "--port",
        str(port),
        "--directory",
        str(directory),
        "--username",
        username,
        "--password",
        password,
    ]
    if permissions:
        command.extend(["--permissions", permissions])
    logger.log(level=log_levels.MODULE_DEBUG, msg="Starting FTP server as process")

    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)


def start_remote_server_as_process(
    connection: "Connection",
    ip: ip_address,
    port: int,
    directory: Union[Path, str],
    username: str,
    password: str,
    python_executable: Optional[str] = None,
    permissions: Optional[str] = None,
) -> "RemoteProcess":
    """
    Start server as process.

    :param ip: IP address for the server to work on.
    :param port: Port for the server to listen.
    :param directory: Path to directory which server should share.
    :param username: Username on which client should login.
    :param password: Password for a user to login.
    :param python_executable: Executable python
    :param permissions: User permissions, indicating which operations are allowed.
    :return Object of server process.
    """
    if not isinstance(connection, (RPyCConnection, LocalConnection)) and not python_executable:
        raise FTPModuleExceptions("Python Executable cannot be None")
    python_executable = python_executable if python_executable else connection.modules().sys.executable
    command = [
        python_executable,
        "-m",
        "mfd_ftp.server",
        "--ip",
        str(ip),
        "--port",
        str(port),
        "--directory",
        str(directory),
        "--username",
        username,
        "--password",
        password,
    ]

    if permissions:
        command.extend(["--permissions", permissions])
    logger.log(level=log_levels.MODULE_DEBUG, msg="Starting FTP server as process")

    cmd_exec = " ".join(command)

    process = connection.start_process(command=cmd_exec, stderr_to_stdout=True, log_file=False)
    _validate_arguments_correctness(process=process)
    return process
