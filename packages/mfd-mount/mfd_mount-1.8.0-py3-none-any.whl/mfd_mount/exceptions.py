# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Module for exceptions."""

import subprocess


class MountException(Exception):
    """Handle mounting exceptions."""


class MountConnectedOSNotSupportedException(MountException):
    """Handle connected OS not supported exceptions."""


class NFSMountException(MountException, subprocess.CalledProcessError):
    """Handle NFS exceptions."""


class CIFSMountException(MountException, subprocess.CalledProcessError):
    """Handle CIFS exceptions."""


class SSHFSMountException(MountException, subprocess.CalledProcessError):
    """Handle SSHFS exceptions."""


class TMPFSMountException(MountException, subprocess.CalledProcessError):
    """Handle TMPFS exceptions."""


class HUGETLBFSMountException(MountException, subprocess.CalledProcessError):
    """Handle HUGELBFS exceptions."""


class MountTypeNotSupported(MountException):
    """Handle not supported mount type exception."""


class UnmountException(MountException, subprocess.CalledProcessError):
    """Handle unmount exceptions."""


class CIFSUpdatingNSMBConfFileException(MountException):
    """Handle updating NSMB Config file exceptions."""
