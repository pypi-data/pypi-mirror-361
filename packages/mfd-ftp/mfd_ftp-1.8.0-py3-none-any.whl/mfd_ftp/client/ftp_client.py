# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Client class for FTP and starting client as process."""

import json
import logging
import subprocess
import sys
from ftplib import FTP
from ipaddress import IPv4Address, IPv6Address, ip_address
from pathlib import Path
from time import perf_counter
from typing import Union, Dict, Any, Optional, TYPE_CHECKING

from mfd_common_libs import add_logging_level, log_levels, TimeoutCounter
from mfd_connect import RPyCConnection, LocalConnection
from mfd_ftp.util.exceptions import FTPModuleExceptions


if TYPE_CHECKING:
    from mfd_connect.process import RemoteProcess
    from mfd_connect import Connection

bits_in_byte = 8

logger = logging.getLogger("mfd_ftp_client")
add_logging_level("MODULE_DEBUG", log_levels.MODULE_DEBUG)


class Client:
    """FTP connected client class."""

    def __init__(
        self,
        ip: Union[IPv4Address, IPv6Address],
        port: int,
        username: str,
        password: str,
        task: str,
        source: str,
        destination: str,
        timeout: Optional[int] = None,
    ) -> None:
        """FTP connected client class.

        :param ip: Address of the FTP server.
        :param port: Number of a port on which server is running.
        :param username: Username for the server to login.
        :param password: Password for the user.
        :param task: Task for the client, can either be 'send' or 'receive'.
        :param source: File to either receive or send.
        :param destination: Destination for the received or sent file.
        :param timeout: Timeout in seconds for operations, like connection attempt, or transfer.
        :return: None
        """
        self._task = task
        self._source = source
        self._destination = destination

        kwargs = {} if timeout is None else {"timeout": timeout}
        self._client = FTP(**kwargs)
        self._client.connect(host=str(ip), port=port)
        self._client.login(user=username, passwd=password)

    def run(self) -> Dict[str, int]:
        """
        Execute sending or receiving file.

        :return: Transfer speed in bits per second and elapsed time in seconds.
        """
        data = None
        if self._task == "send":
            logger.log(level=log_levels.MODULE_DEBUG, msg="Sending file")
            data = self._send_file()
            logger.log(level=log_levels.MODULE_DEBUG, msg="File was sent")

        elif self._task == "receive":
            logger.log(level=log_levels.MODULE_DEBUG, msg="Receiving file")
            data = self._receive_file()
            logger.log(level=log_levels.MODULE_DEBUG, msg="File was received")

        return data

    def _send_file(self) -> Dict[str, Union[int, int]]:
        """Send file to the server location and save it as destination name.

        :return: Transfer speed in bits per second and elapsed time in seconds.
        """
        source = Path(self._source)
        with source.open("rb") as f:
            start_time = perf_counter()
            self._client.storbinary(f"STOR {str(self._destination)}", f)
            end_time = perf_counter()
        elapsed_time = end_time - start_time
        transfer_speed = source.stat().st_size * bits_in_byte / elapsed_time
        logger.log(
            level=log_levels.MODULE_DEBUG,
            msg=f"elapsed_time: {float(elapsed_time)}, transfer_speed: {int(transfer_speed)}",
        )
        return {"elapsed_time": int(elapsed_time), "transfer_speed": int(transfer_speed)}

    def _receive_file(self) -> Dict[str, Union[int, int]]:
        """Receive file form the server.

        :return: Transfer speed in bits per second and elapsed time in seconds.
        """
        destination = Path(self._destination)
        with destination.open("wb") as f:
            start_time = perf_counter()
            self._client.retrbinary(f"RETR {self._source}", f.write)
            end_time = perf_counter()
        elapsed_time = end_time - start_time
        transfer_speed = destination.stat().st_size * bits_in_byte / elapsed_time
        logger.log(
            level=log_levels.MODULE_DEBUG,
            msg=f"elapsed_time: {float(elapsed_time)}, transfer_speed: {int(transfer_speed)}",
        )
        return {"elapsed_time": int(elapsed_time), "transfer_speed": int(transfer_speed)}


def _start_client(config: Dict[str, Any]) -> None:
    """
    Execute tool, creating client and run it's transfer.

    :param config: configuration containing all the parameters for client creation. Passed from _parse_args in __main__.
    """
    verbose = config.pop("verbose")
    client = Client(**config)
    data = client.run()
    if verbose:
        logger.info(json.dumps(data))


def start_client_as_process(
    ip: ip_address,
    port: int,
    task: str,
    source: str,
    destination: str,
    username: str,
    password: str,
    timeout: int = None,
    verbose: bool = True,
) -> subprocess.Popen:
    """Start client as background process.

    :param ip: Address of the FTP server.
    :param port: Number of a port on which server is running.
    :param task: Task for the client, can either be 'send' or 'receive'.
    :param source: File to either receive or send.
    :param destination: Destination for the received or sent file.
    :param username: Username for the server to login.
    :param password: Password for the user.
    :param timeout: Timeout in seconds for operations, like connection attempt, or transfer.
    :param verbose: If True, log transfer information in JSON format. Default True.
    """
    command = [
        str(sys.executable),
        "-m",
        "mfd_ftp.client",
        "--ip",
        str(ip),
        "--port",
        str(port),
        "--task",
        task,
        "--source",
        source,
        "--destination",
        destination,
        "--username",
        username,
        "--password",
        password,
    ]
    if timeout:
        command.extend(["--timeout", str(timeout)])
    if verbose:
        command.append("--verbose")

    logger.log(level=log_levels.MODULE_DEBUG, msg="Starting FTP client process...")

    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@staticmethod
def _validate_arguments_correctness(process: "RemoteProcess", ftp_task: str) -> None:
    """Check correctness of passed arguments after start of process.

    :param process: FTPProcess
    :raises: FTPModuleException if passed incorrect args
    """
    valid_output = {"send": "File was sent", "receive": "File was received"}
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
        elif valid_output[ftp_task] in output:
            return
        else:
            logger.log(level=log_levels.MODULE_DEBUG, msg=output)
            raise FTPModuleExceptions(f"Server/client is not running: {output}")


def start_remote_client_as_process(
    connection: "Connection",
    ip: ip_address,
    port: int,
    task: str,
    source: str,
    destination: str,
    username: str,
    password: str,
    python_executable: str = None,
    timeout: int = None,
    verbose: bool = True,
) -> "RemoteProcess":
    """
    Start client as background process.

    :param connection: FTP Connection
    :param ip: Address of the FTP server.
    :param port: Number of a port on which server is running.
    :param task: Task for the client, can either be 'send' or 'receive'.
    :param source: File to either receive or send.
    :param destination: Destination for the received or sent file.
    :param username: Username for the server to login.
    :param password: Password for the user.
    :param python_executable: Executable python.
    :param timeout: Timeout in seconds for operations, like connection attempt, or transfer.
    :param verbose: If True, log transfer information in JSON format. Default True.
    :return Object of server process.
    """
    if not isinstance(connection, (RPyCConnection, LocalConnection)) and not python_executable:
        raise FTPModuleExceptions("Python Executable cannot be None")
    python_executable = python_executable if python_executable else connection.modules().sys.executable
    command = [
        python_executable,
        "-m",
        "mfd_ftp.client",
        "--ip",
        str(ip),
        "--port",
        str(port),
        "--task",
        task,
        "--source",
        source,
        "--destination",
        destination,
        "--username",
        username,
        "--password",
        password,
    ]

    if timeout:
        command.extend(["--timeout", str(timeout)])
    if verbose:
        command.append("--verbose")

    cmd_exec = " ".join(command)

    logger.log(level=log_levels.MODULE_DEBUG, msg="Starting FTP client process...")

    process = connection.start_process(command=cmd_exec, stderr_to_stdout=True, log_file=True)
    _validate_arguments_correctness(process=process, ftp_task=task)
    return process
