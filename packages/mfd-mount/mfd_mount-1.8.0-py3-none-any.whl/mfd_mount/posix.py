# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for posix mount."""

import logging
import subprocess
from pathlib import Path
from typing import Union, Optional

from mfd_mount import Mount
from mfd_mount.base import _unmount_context_manager
from mfd_mount.exceptions import (
    NFSMountException,
    CIFSMountException,
    SSHFSMountException,
    TMPFSMountException,
    HUGETLBFSMountException,
    UnmountException,
)

logger = logging.getLogger(__name__)


class PosixMount(Mount):
    """
    Class responsible for mounting fileshares on Posix OS.

    Usage example:
    >>> mounter = PosixMount(connection=LocalConnection())
    >>> mounter.is_mounted("/mnt/fileshare")
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
        """
        Mount CIFS share.

        :param mount_point: Path to directory for mount, eg. /mnt/shared
        :param share_path: Path to mount including server eg. //10.10.10.10/to_share
        :param username: Username to share if required
        :param password: Password to share if required
        :raises CIFSMountException: on failure
        """
        self._generic_mount("cifs", mount_point, share_path, username, password)

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

        :param mount_point: Path to directory for mount, eg. /mnt/shared
        :param share_path: Path to mount including server eg. 10.10.10.10:/to_share
        :param username: Username to share if required
        :param password: Password to share if required
        :raises NFSMountException: on failure
        """
        self._generic_mount("nfs", mount_point, share_path, username, password)

    @_unmount_context_manager
    def mount_sshfs(
        self,
        *,
        mount_point: Union[Path, str],
        share_path: Union[Path, str],
        username: str,
        password: str,
    ) -> None:
        """
        Mount SSH share.

        :param mount_point: Path to directory for mount, eg. /mnt/shared
        :param share_path: Path to mount including server eg. 10.10.10.10:/to_share
        :param username: Required username to share
        :param password: Required password to share
        :raises SSHFSMountException: on failure
        """
        logger.debug(f"Mounting SSHFS share {share_path} on {mount_point}.")
        sshfs_command = "sshfs -o password_stdin -o StrictHostKeyChecking=no"
        command = f"{sshfs_command} {username}@{share_path} {mount_point} <<<'{password}'"

        self._conn.execute_command(command, shell=True, custom_exception=SSHFSMountException)
        logger.debug(f"Mounted SSHFS share {share_path} on {mount_point}.")

    @_unmount_context_manager
    def mount_tmpfs(
        self,
        *,
        mount_point: Union[Path, str],
        share_path: Union[Path, str],
        params: str = "",
    ) -> None:
        """
        Mount TMP share.

        :param mount_point: Path to directory for mount, eg. /mnt/shared
        :param share_path: Path to mount including server eg. 10.10.10.10:/to_share
        :param params: Additional parameters for the file system mount command.
        :raises TMPFSMountException: on failure
        """
        self._generic_mount(mount_method="tmpfs", mount_point=mount_point, share_path=share_path, params=params)

    @_unmount_context_manager
    def mount_hugetlbfs(self, *, mount_point: Union[Path, str], share_path: Union[Path, str], params: str = "") -> None:
        """
        Mount HUGELB share.

        :param mount_point: Path to directory for mount, eg. /mnt/shared
        :param share_path: Path to mount including server eg. 10.10.10.10:/to_share
        :param params: Additional parameters for the file system mount command.
        :raises HUGELBFSMountException: on failure
        """
        self._generic_mount(mount_method="hugetlbfs", mount_point=mount_point, share_path=share_path, params=params)

    def _generic_mount(
        self,
        mount_method: str,
        mount_point: Union[Path, str],
        share_path: Union[Path, str],
        username: Optional[str] = None,
        password: Optional[str] = None,
        params: Optional[str] = None,
    ) -> None:
        """
        Mount share using generic method for posix mount program.

        :param mount_point: Path to directory for mount
        :param share_path: Path to mount including server
        :param username: Username to share if required
        :param password: Password to share if required
        :param params: Additional parameters for mount
        :raises NFSMountException: on nfs failure
        :raises CIFSMountException: on cifs failure
        :raises TMPFSMountException: on tmpfs failure
        :raises HUGELBFSMountException: on hugelbfs failure
        """
        logger.debug(f"Mounting {mount_method.upper()} share {share_path} on {mount_point}.")
        options = ""
        if username:
            options = f"-o username={username}"
            if password:
                options += f",password={password}"
        if params:
            options += f"{params}"
        mount_command_list = [f"mount -t {mount_method}", str(share_path), str(mount_point)]
        if options:
            # insert options after mount_method
            mount_command_list.insert(1, options)

        exceptions = {
            "nfs": NFSMountException,
            "cifs": CIFSMountException,
            "tmpfs": TMPFSMountException,
            "hugetlbfs": HUGETLBFSMountException,
        }
        self._conn.execute_command(" ".join(mount_command_list), custom_exception=exceptions[mount_method])
        logger.debug(f"Mounted {mount_method.upper()} share {share_path} on {mount_point}.")

    def is_mounted(self, mount_point: Union[Path, str]) -> bool:
        """Check if given mount_point is mounted.

        :param mount_point: Path to directory to check if is mounted
        :return: bool value: True if mount_point is mounted, False if not
        """
        try:
            output = self._conn.execute_command(f"df {mount_point}").stdout
            if mount_point not in output:
                return False
            return True
        except subprocess.CalledProcessError:
            return False

    def umount(self, mount_point: Union[Path, str]) -> None:
        """
        Unmount share using posix umount program.

        :param mount_point: Path to directory for mounted share
        :raises UnmountException: on failure
        """
        logger.debug(f"Unmounting {mount_point} mounting point.")
        self._conn.execute_command(f"umount {mount_point}", custom_exception=UnmountException)
        logger.debug(f"Unmounted {mount_point} mounting point.")
