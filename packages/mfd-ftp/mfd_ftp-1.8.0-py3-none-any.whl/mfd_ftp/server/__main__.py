# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Starting Module for ftp server."""

import sys
import logging
from mfd_common_libs import add_logging_level, log_levels
from .ftp_server import _parse_args, _get_server

logger = logging.getLogger(__name__)
add_logging_level("MODULE_DEBUG", log_levels.MODULE_DEBUG)

try:
    server = _get_server(**_parse_args())
    server.serve_forever()
except KeyboardInterrupt:
    logger.log(level=log_levels.MODULE_DEBUG, msg="Server shutdown.", file=sys.stderr)
    sys.exit(0)
