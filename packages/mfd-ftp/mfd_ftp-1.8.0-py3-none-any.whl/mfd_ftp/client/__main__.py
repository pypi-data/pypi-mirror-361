# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Starting Module for ftp client."""

import sys
import logging
from mfd_common_libs import add_logging_level, log_levels
from typing import Dict, Any
from ipaddress import ip_address
from argparse import ArgumentParser

from .ftp_client import _start_client

logger = logging.getLogger("mfd_ftp_client")
add_logging_level("MODULE_DEBUG", log_levels.MODULE_DEBUG)
logger.setLevel(log_levels.MODULE_DEBUG)

handler = logging.StreamHandler()
handler.setLevel(log_levels.MODULE_DEBUG)

handler_stdout = logging.StreamHandler(sys.stdout)
handler_stdout.setLevel(logging.INFO)

logger.addHandler(handler)
logger.addHandler(handler_stdout)


def _parse_args() -> Dict[str, Any]:
    """
    Parse commandline arguments.

    :return: Config for the tool execution.
    """
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ip",
        metavar="<ip>",
        required=True,
        type=ip_address,
        help="IP address of the server for the client to connect to.",
    )
    parser.add_argument(
        "--port",
        metavar="<port>",
        type=int,
        default=21,
        help="Network port of the server, if not given default port %(default)s is passed.",
    )
    parser.add_argument(
        "--task",
        metavar="<task>",
        required=True,
        type=str,
        choices=["send", "receive"],
        help="Task for the client, can either receive or send file.",
    )
    parser.add_argument(
        "--source", metavar="<source>", required=True, type=str, help="File name or file path of the source file."
    )
    parser.add_argument(
        "--destination", metavar="<destination>", required=True, type=str, help="File name for the destination file."
    )
    parser.add_argument("--username", metavar="<username>", required=True, type=str, help="Username.")
    parser.add_argument("--password", metavar="<password>", required=True, type=str, help="Password for the user.")
    parser.add_argument(
        "--timeout",
        metavar="<timeout>",
        type=int,
        help="Timeout in seconds for operations, like connection attempt, or transfer.",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="If given, print additional information to STDOUT in JSON format."
    )
    return vars(parser.parse_args())


try:
    _start_client(_parse_args())
except KeyboardInterrupt:
    logger.log(level=log_levels.MODULE_DEBUG, msg="Client shutdown.")
    sys.exit(0)
