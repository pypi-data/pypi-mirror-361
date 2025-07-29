# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for esxi mount."""

import re
import logging
from pathlib import Path
from typing import Union, Optional

from mfd_mount import Mount
from mfd_mount.base import _unmount_context_manager
from mfd_mount.exceptions import NFSMountException, MountException, MountTypeNotSupported, UnmountException

logger = logging.getLogger(__name__)


class ESXiMount(Mount):
    """Class for mounting on ESXI 7.0."""

    def mount_cifs(
        self,
        *,
        mount_point: Union[Path, str],
        share_path: Union[Path, str],
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """
        Mount CIFS share.

        CIFS method is unsupported on ESXi.
        :param mount_point: Path to directory for mount
        :param share_path: Path to mount including server
        :param username: Username to share if required
        :param password: Password to share if required
        :raises MountTypeNotSupported: if CIFS mount method is unsupported
        """
        raise MountTypeNotSupported("CIFS mount is not supported for ESXi. Use other mount method.")

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

        :param mount_point: Volume name for new mount eg. nfsstore-12
        :param share_path: Path to mount including server eg. 10.10.10.10:/to_share or 10.10.10.10/to_share
        :param username: UNUSED
        :param password: UNUSED
        :raises NFSMountException: on failure
        """
        logger.debug(f"Mounting NFS share {share_path} on {mount_point}.")
        if username or password:
            logger.debug("Authentication for NFS on ESXi is not supported. Skipping values for user/pass")

        share_path = str(share_path)
        if ":" in share_path:
            host, share = share_path.split(":")
        else:
            separator_index = share_path.find("/")
            # -1 - not found
            # splitting by / first
            if separator_index != -1:
                # 10.10.10.10/mount/point
                host = share_path[:separator_index]  # 10.10.10.10
                share = share_path[separator_index:]  # /mount/point
            else:
                raise MountException("Share path is in incorrect format.")
        mount_command_list = ["esxcli storage nfs add", f"-H {host}", f"-s {share}", f"-v {mount_point}"]
        self._conn.execute_command(" ".join(mount_command_list), custom_exception=NFSMountException)
        logger.debug(f"Mounted NFS share {share_path} as {mount_point}.")

    def is_mounted(self, mount_point: Union[Path, str]) -> bool:
        """Check if given mount_point is mounted.

        :param mount_point: Path to directory to check if is mounted
        :return: bool value: True if mount_point is mounted, False if not
        """
        output = self._conn.execute_command("esxcli storage nfs list").stdout

        mount_match = re.search(rf"^{mount_point} ", output, re.MULTILINE)

        return True if mount_match else False

    def umount(self, mount_point: Union[Path, str]) -> None:
        """
        Unmount share using esxcli program.

        :param mount_point: Volume name
        :raises UnmountException: on failure
        """
        logger.debug(f"Unmounting {mount_point} mounting point.")
        self._conn.execute_command(f"esxcli storage nfs remove -v {mount_point}", custom_exception=UnmountException)
        logger.debug(f"Unmounted {mount_point} mounting point.")
