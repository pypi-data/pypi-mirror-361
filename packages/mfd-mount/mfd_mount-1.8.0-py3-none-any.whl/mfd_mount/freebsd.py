# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for FreeBSD mount."""

import logging
from pathlib import Path
from typing import Union, Optional

from mfd_common_libs import log_levels

from mfd_mount import PosixMount
from mfd_mount.base import _unmount_context_manager
from mfd_mount.exceptions import CIFSMountException, CIFSUpdatingNSMBConfFileException, MountException

logger = logging.getLogger(__name__)


class FreeBSDMount(PosixMount):
    """
    Class responsible for mounting fileshares on Posix OS.

    Usage example:
    >>> mounter = FreeBSDMount(connection=LocalConnection())
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
        :param share_path: Path to mount including server eg. 10.10.10.10/to_share
        :param username: Username to share is mandatory for FreeBSDMount
        :param password: Password to share if required
        :raises CIFSMountException: on failure
        :raises MountException: when username is not given
        """
        if not username:
            raise MountException("Username is mandatory for CIFS mount method!")

        logger.debug(f"Mounting CIFS share {share_path} on {mount_point}.")

        host = str(share_path).split("/")[0]

        mount_command_list = ["mount_smbfs", f"-I {host}", f"//{username}@{share_path}", str(mount_point)]
        if password:
            logger.debug(f"Check if nsmb.conf file contains password for user: {username} at host:{host}")
            self._configure_nsmb_conf_file(username, password, host)

        self._conn.execute_command(" ".join(mount_command_list), custom_exception=CIFSMountException)
        logger.debug(f"Mounted CIFS share {share_path} on {mount_point}.")

    def _configure_nsmb_conf_file(self, username: str, password: str, host: str) -> None:
        """
        Configure nsmb.conf file with proper host, user and password.

        :param username: Username to share
        :param password: Password to share
        :param host: Host - IP address
        :raises CIFSUpdatingNSMBConfFileException: if updating nsmb.conf file failed
        """
        nsmb_conf = self._conn.path("/etc", "nsmb.conf")
        nsmb_content = nsmb_conf.read_text()

        credentials = f"[{host}:{username.upper()}]\npassword={password}"
        if credentials in nsmb_content:
            logger.log(level=log_levels.MODULE_DEBUG, msg="Password found in nsmb.conf file")
            return

        logger.log(level=log_levels.MODULE_DEBUG, msg="Writing credentials to nsmb.conf")
        cmd = f"echo '[{host}:{username.upper()}]' >> {nsmb_conf}; echo 'password={password}' >> {nsmb_conf}"
        self._conn.execute_command(cmd)

        logger.log(level=log_levels.MODULE_DEBUG, msg="Check if nsmb.conf has updated credentials")
        if credentials not in nsmb_conf.read_text():
            raise CIFSUpdatingNSMBConfFileException("nsmb.conf file does not have credentials. Updating file failed!")
