# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Utility module for ftp operations."""

import ftplib
import logging
import os
import typing
from ipaddress import ip_address

from mfd_ftp.util.exceptions import FTPModuleExceptions

logger = logging.getLogger(__name__)


class FTPUtils(object):
    """Utility for FTP operations."""

    def __init__(self, ip: str, username: str, password: str) -> None:
        """
        Initialize FTPUtils.

        :param ip: Address of FTP Server
        :param username: Username to authentication
        :param password: Password to authentication
        """
        self._ip = ip_address(ip)
        self._username = username
        self._password = password

    def _ftp_login(self) -> ftplib.FTP:
        """
        Connect with FTP server.

        :return: FTP client object
        :raises: FTPModuleExceptions exceptions on failure
        """
        logger.debug(f"FTP Login, IP is {self._ip}...")
        try:
            connection = ftplib.FTP(self._ip, self._username, self._password)
        except ftplib.all_errors as e:
            logger.debug("Error occurred while connecting to FTP server:")
            logger.debug(e)
            raise FTPModuleExceptions("Error occurred while connecting to FTP server") from e
        return connection

    def return_dirs(self, catalog: str = "/") -> typing.List:
        """
        Return list of directory on FTP.

        :param catalog: Directory to check
        :return: List of directories in directory
        :raises: FTPModuleExceptions exceptions on failure
        """
        logger.debug("Connecting via FTP....")
        with self._ftp_login() as connection:
            try:
                connection.cwd(catalog)
                directories = []
                connection.retrlines("LIST", callback=directories.append)
            except ftplib.all_errors as e:
                logger.debug("Error occurred while polling for list of dirs on FTP:")
                logger.debug(e)
                raise FTPModuleExceptions("Error occurred while polling for list of dirs on FTP") from e
            return directories

    def is_directory_on_ftp(self, directory: str) -> bool:
        """
        Check if directory is on FTP server.

        :param directory: Directory to check
        :return: Status of existence
        """
        logger.debug(f"It will be check if {directory} is already present on FTP")
        usb_content = self.return_dirs("/")
        for line in usb_content:
            if directory == line:
                logger.debug(f"{directory} found on FTP")
                return True
        logger.debug(f"{directory} not found on FTP")
        return False

    def copy_files_to_ftp(self, source_directory: str, destination_directory: str) -> bool:
        """
        Download files from directory into FTP.

        :param source_directory: Directory to copy
        :param destination_directory: Directory where files will be copied
        :return: Status of copying
        :raises: FTPModuleExceptions exceptions on failure
        """
        with self._ftp_login() as connection:
            try:
                connection.sendcmd(f"MKDIR {destination_directory}")
                src_files = os.listdir(f"{source_directory}")
                for file_name in src_files:
                    full_file_name = os.path.join(source_directory, file_name)
                    logger.debug(f"Copying {full_file_name} ...")
                    if os.path.isfile(full_file_name):
                        connection.storbinary(f"STOR {destination_directory}/{file_name}", open(full_file_name))
            except ftplib.all_errors as e:
                logger.debug("Error occurred while polling for list of dirs on FTP:")
                logger.debug(e)
                raise FTPModuleExceptions("Error occurred while polling for list of dirs on FTP") from e
        logger.debug("FTP session closed")
        return True
