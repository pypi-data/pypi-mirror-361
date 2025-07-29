# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Constants and Enum for Windows Registry module."""

from enum import Enum


class PropertyType(Enum):
    """Enum class for Property Type of Windows Registry."""

    NONE = "None"
    BINARY = "Binary"
    DWORD = "DWord"
    QWORD = "QWord"
    STRING = "String"
    EXPANDSTRING = "ExpandString"
    MULTISTRING = "MultiString"
    UNKNOWN = "Unknown"


class BuffersAttribute(Enum):
    """Enum class for Buffers Attribute of Windows Registry."""

    DEFAULT = "default"
    MIN = "min"
    MAX = "max"
    NONE = "None"


NIC_REGISTRY_BASE_PATH = r"hklm:\system\CurrentControlSet\control\class\{4D36E972-E325-11CE-BFC1-08002BE10318}"
NIC_SWITCHES_REGISTRY_BASE_PATH = rf"{NIC_REGISTRY_BASE_PATH}\%s\NicSwitches\0"
PROSET_PATH = r"HKLM:\Software\Intel"
PROSET_KEY_LIST = ["Basedrivers", "NETWORK_SERVICES", "Prounstl"]
