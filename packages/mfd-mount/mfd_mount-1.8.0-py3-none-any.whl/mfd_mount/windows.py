# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for windows mount."""

import logging
import subprocess
from pathlib import Path
from typing import Union, Optional

from mfd_mount import Mount
from mfd_mount.base import _unmount_context_manager
from mfd_mount.exceptions import NFSMountException, CIFSMountException, UnmountException

logger = logging.getLogger(__name__)


class WindowsMount(Mount):
    """
    Class responsible for mounting fileshares on Windows OS.

    Usage example:
    >>> mounter = WindowsMount(connection=LocalConnection())
    >>> mounter.is_mounted("Z:")
    True
    """

    @_unmount_context_manager
    def mount_cifs(
        self,
        *,
        mount_point: Union[Path, str],
        share_path: Union[Path, str],
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        r"""
        Mount CIFS share.

        :param mount_point: Path to directory for mount, eg. Z:
        :param share_path: Path to mount including server, eg. \\10.10.10.10\to_share
        :param username: Username to share if required
        :param password: Password to share if required
        :raises CIFSMountException: on failure
        """
        logger.debug(f"Mounting CIFS share {share_path} on {mount_point}.")
        options = ""
        if username:
            options = f"/user:{username}"
            if password:
                options += f" {password}"

        mount_command_list = ["net use", str(mount_point), str(share_path), "/persistent:no"]
        if options:
            mount_command_list.append(options)

        self._conn.execute_command(" ".join(mount_command_list), custom_exception=CIFSMountException)
        logger.debug(f"Mounted CIFS share {share_path} on {mount_point}.")

    @_unmount_context_manager
    def mount_nfs(
        self,
        *,
        mount_point: Union[Path, str],
        share_path: Union[Path, str],
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """
        Mount NFS share.

        :param mount_point: Path to directory for mount, eg. Z:
        :param share_path: Path to mount including server eg. 10.10.10.10:/to_share
        :param username: Username to share if required
        :param password: Password to share if required
        :raises NFSMountException: on failure
        """
        logger.debug(f"Mounting NFS share {share_path} on {mount_point}.")
        options = ""
        if username:
            options = f"-u:{username}"
            if password:
                options += f" -p:{password}"
        mount_command_list = ["mount", str(share_path), str(mount_point)]
        if options:
            # insert options after 'mount'
            mount_command_list.insert(1, options)
        self._conn.execute_command(" ".join(mount_command_list), custom_exception=NFSMountException)
        logger.debug(f"Mounted NFS share {share_path} on {mount_point}.")

    def is_mounted(self, mount_point: Union[Path, str]) -> bool:
        """Check if given mount_point is mounted.

        :param mount_point: Path to directory to check
        :return: bool value: True if mount_point is mounted, False if not
        """
        try:
            self._conn.execute_command(f"net use {mount_point}")
            return True
        except subprocess.CalledProcessError:
            return False

    def umount(self, mount_point: Union[Path, str]) -> None:
        """
        Unmount share using net use program.

        :param mount_point: Path to directory for mounted share
        :raises UnmountException: on failure
        """
        logger.debug(f"Unmounting {mount_point} mounting point.")
        result = self._conn.execute_command(f"net use {mount_point} /delete", custom_exception=UnmountException)
        if "was deleted successfully" not in result.stdout:
            raise UnmountException(1, "net use", "", "Confirmation of unmount not found")
        logger.debug(f"Unmounted {mount_point} mounting point.")
