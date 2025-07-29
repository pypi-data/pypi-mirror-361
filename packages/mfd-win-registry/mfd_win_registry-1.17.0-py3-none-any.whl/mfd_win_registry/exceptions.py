# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Exceptions for Windows Registry."""

import subprocess


class WindowsRegistryException(Exception):
    """Handle WindowsRegistry Exceptions."""


class WindowsRegistryConnectedOSNotSupported(WindowsRegistryException):
    """Handle WindowsRegistry unsupported os exceptions."""


class WindowsRegistryExecutionError(WindowsRegistryException, subprocess.CalledProcessError):
    """Handle WindowsRegistry Execution errors."""
