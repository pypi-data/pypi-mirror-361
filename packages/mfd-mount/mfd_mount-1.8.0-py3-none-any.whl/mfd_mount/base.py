# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for MFD Mount implementation."""

from pathlib import Path
from typing import Optional, Callable
from typing import TYPE_CHECKING
from typing import Union
from .exceptions import MountConnectedOSNotSupportedException
from mfd_typing.os_values import OSName

if TYPE_CHECKING:
    from mfd_connect import Connection


def _unmount_context_manager(func: Callable) -> Callable:
    """
    Create decorator function enabling mount methods to be executed as context manager as well as through a usual call.

    This decorator is supposed to be used in internal implementation only.

    Usage example:
    @_available_as_context_manager
    def mount_nfs(...):
        ...

    >>> mounter = Mount(connection=LocalConnection())
    >>> with mounter.mount_nfs(mount_point="/mnt/shared", share_path="10.10.10.10:/to_share"):
    >>>     ...  # will unmount share afterwards
    """

    def decorator_func(self, *args, **kwargs):  # noqa: ANN001, ANN201, ANN202
        mount_point = kwargs.get("mount_point")
        func(self, *args, **kwargs)

        class ContextManager(type(self)):
            """Context manager helper class."""

            def __enter__(self):
                pass

            def __exit__(self, exc_type, exc_val, exc_tb):  # noqa: ANN001
                self.umount(mount_point)

        return ContextManager(self._conn)

    return decorator_func


class Mount:
    """
    Class responsible for mounting fileshares on OS.

    Usage example:
    >>> mounter = Mount(connection=LocalConnection())
    >>> mounter.is_mounted("/mnt/fileshare")
    True

    """

    def __new__(cls, connection: "Connection"):
        """
        Choose Mount subclass based on connected OS.

        :param connection: Connection object of host on which mounting operations will be executed.
        :return: Instance of Mount subclass.
        :raises MountConnectedOSNotSupportedException: when connected OS is not supported by Mount.
        """
        if cls == Mount:
            from .posix import PosixMount
            from .windows import WindowsMount
            from .esxi import ESXiMount
            from .freebsd import FreeBSDMount

            os_name = connection.get_os_name()
            os_name_to_class = {
                OSName.WINDOWS: WindowsMount,
                OSName.LINUX: PosixMount,
                OSName.FREEBSD: FreeBSDMount,
                OSName.ESXI: ESXiMount,
            }

            if os_name not in os_name_to_class.keys():
                raise MountConnectedOSNotSupportedException("OS of connected client not supported")

            mount_class = os_name_to_class.get(os_name)
            return super(Mount, cls).__new__(mount_class)
        else:
            return super(Mount, cls).__new__(cls)

    def __init__(self, connection: "Connection") -> None:
        """
        Initialize Mount object.

        :param connection: Connection object of host on which mounting operations will be executed.
        """
        self._conn = connection

    @_unmount_context_manager
    def mount_cifs(
        self,
        *,
        mount_point: Union[Path, str],
        share_path: Union[Path, str],
        username: Optional[str],
        password: Optional[str],
    ) -> None:
        """
        Mount CIFS share.

        :param mount_point: Path to directory for mount
        :param share_path: Path to mount including server
        :param username: Username to share if required
        :param password: Password to share if required
        :raises CIFSMountException: on failure
        """
        raise NotImplementedError

    @_unmount_context_manager
    def mount_nfs(
        self,
        *,
        mount_point: Union[Path, str],
        share_path: Union[Path, str],
        username: Optional[str],
        password: Optional[str],
    ) -> None:
        """
        Mount NFS share.

        :param mount_point: Path to directory for mount, eg. Z: for Windows, /mnt/shared for Posix
        :param share_path: Path to mount including server eg. 10.10.10.10:/to_share
        :param username: Username to share if required
        :param password: Password to share if required
        :raises NFSMountException: on failure
        """
        raise NotImplementedError

    @_unmount_context_manager
    def mount_sshfs(
        self,
        *,
        mount_point: Union[Path, str],
        share_path: Union[Path, str],
        username: Optional[str],
        password: Optional[str],
    ) -> None:
        """
        Mount SSH share.

        :param mount_point: Path to directory for mount, eg. /mnt/shared
        :param share_path: Path to mount including server eg. 10.10.10.10:/to_share
        :param username: Required username to share
        :param password: Required password to share
        :raises SSHFSMountException: on failure
        """
        raise NotImplementedError

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
        raise NotImplementedError

    @_unmount_context_manager
    def mount_hugetlbfs(
        self,
        *,
        mount_point: Union[Path, str],
        share_path: Union[Path, str],
        params: str = "",
    ) -> None:
        """
        Mount HUGETLB share.

        :param mount_point: Path to directory for mount, eg. /mnt/shared
        :param share_path: Path to mount including server eg. 10.10.10.10:/to_share
        :param params: Additional parameters for the file system mount command
        :raises HUGETLBFSMountException: on failure
        """
        raise NotImplementedError

    def is_mounted(self, mount_point: Union[Path, str]) -> bool:
        """
        Check if given mount_point is mounted.

        :param mount_point: Path to directory to check if is mounted
        :return: bool value: True if mount_point is mounted, False if not
        """
        raise NotImplementedError

    def umount(self, mount_point: Union[Path, str]) -> None:
        """
        Unmount share using correct umount program.

        :param mount_point: Path to directory for mounted share
        :raises UnmountException: on failure
        """
        raise NotImplementedError
