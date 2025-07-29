# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Base FTP traffic."""

import logging
from abc import ABC
from time import sleep
from typing import TYPE_CHECKING, Callable, Any, Dict

from mfd_common_libs import TimeoutCounter, log_levels, add_logging_level
from mfd_ftp.util.exceptions import FTPModuleExceptions
from mfd_traffic_manager.base import Traffic


if TYPE_CHECKING:
    from mfd_connect.process import RemoteProcess

logger = logging.getLogger(__name__)
add_logging_level("MODULE_DEBUG", log_levels.MODULE_DEBUG)


class FTPTraffic(Traffic, ABC):
    """Class for common FTP traffic."""

    _process: "RemoteProcess"

    def _get_output(self, process: "RemoteProcess") -> str:
        """Get FTP results from stopped FTP process.

        :param process: Process of connection object, necessary stopped FTP process.
        :raises FTPModuleException: if process is running
        """
        if process.running:
            raise FTPModuleExceptions("Process is still running.")

        if getattr(process, "log_path", None) is not None:
            output = process.log_path.read_text(encoding="ISO-8859-1")
            if process.log_file_stream is not None:
                process.log_file_stream.close()
            logger.log(level=log_levels.MODULE_DEBUG, msg=f"Removing {process.log_path} log file")
            process.log_path.unlink()
        else:
            output = process.stdout_text
            logger.log(level=log_levels.MODULE_DEBUG, msg=f"output: {output}")
        return output

    def stop(self) -> None:
        """
        Stop FTP traffic.

        :return: None
        """
        if not self._process.running:
            return
        self._process.stop(1)
        timeout = TimeoutCounter(5)
        while not timeout:
            if not self._process.running:
                break
        else:
            self._process.kill(1)
            timeout = TimeoutCounter(5)
            while not timeout:
                if not self._process.running:
                    break
            else:
                raise FTPModuleExceptions("Failed to stop FTP process in 10 seconds")

    def run(self, duration: int) -> None:
        """
        Run FTP traffic for specified duration.

        :param duration: duration of traffic in seconds
        :return: None
        """
        timeout = TimeoutCounter(duration)
        self.start()
        while not timeout:
            if not self._process.running:
                break
            sleep(1)
        else:
            self.stop()

    def validate(
        self,
        validation_criteria: Dict[Callable, Dict[str, Any]] = None,
    ) -> bool:
        """
        Validate FTP traffic by specified criteria.

        :param validation_criteria: criteria by which traffic should be validated
        :return: True if traffic is correct according to criteria, False otherwise
        """
        interval_results = self._get_output(self._process)
        return self._validate(interval_results, validation_criteria)
