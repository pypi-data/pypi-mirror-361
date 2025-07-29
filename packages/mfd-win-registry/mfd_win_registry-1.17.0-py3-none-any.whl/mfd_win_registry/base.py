# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Windows Registry module."""

import logging
import re
from copy import deepcopy
from typing import Dict, List, Union, TYPE_CHECKING
from mfd_common_libs import add_logging_level, log_levels, os_supported
from mfd_connect.util.powershell_utils import parse_powershell_list
from mfd_typing import OSName
from .constants import NIC_REGISTRY_BASE_PATH, PropertyType, PROSET_PATH, PROSET_KEY_LIST, BuffersAttribute
from .exceptions import WindowsRegistryExecutionError, WindowsRegistryException

if TYPE_CHECKING:
    from mfd_connect import Connection

logger = logging.getLogger(__name__)
add_logging_level("MODULE_DEBUG", log_levels.MODULE_DEBUG)


class WindowsRegistry:
    """Class to handle registers in Windows."""

    @os_supported(OSName.WINDOWS)
    def __init__(self, connection: "Connection"):
        """
        Initialize connection.

        :param connection: mfd_connect object for remote connection handling
        """
        self._cached_feature_dict: Dict[str, Dict[str, str]] = {}
        self._cached_feature_attributes = {}
        self._cached_saved_params_path = ""
        self._connection = connection

    def _dict_merge(self, a: Dict, b: Dict) -> Dict:
        """Merge two dictionaries.

        Recursively merges dicts. Not just simple a['key'] = b['key'], if
        both a and b have a key whose value is a dict then _dict_merge is called
        on both values and the result stored in the returned dictionary.
        """
        if not isinstance(a, dict) or not isinstance(b, dict):
            raise WindowsRegistryException("The args should be dictionary")
        result = deepcopy(a)
        for k, v in b.items():
            if isinstance(result.get(k), dict):
                result[k] = self._dict_merge(result[k], v)
            else:
                result[k] = deepcopy(v)
        return result

    @staticmethod
    def _get_depth_command(cmd: str, abs_path: str, depth: int = 0) -> str:
        """Get the command based on depth.

        :param cmd: Get-ItemProperty command
        :param abs_path: Path to Windows registry from which to take the properties
        :param depth: How deep go into sub-keys, be careful with big trees and large depth
        :return: Command by adding depth.
        """
        logger.log(level=log_levels.MODULE_DEBUG, msg=r"Adding \* to the command based on depth")
        for i in range(depth):
            dp = "\\*" * (i + 1)
            cmd += f",'{abs_path}{dp}'"
        return cmd

    @staticmethod
    def _get_registry_dict(block: str) -> Dict:
        """Get Output in dictionary format.

        :param block: Output from the get-itemproperty command
        :return: Dictionary with property:value pairs
        """
        logger.log(level=log_levels.MODULE_DEBUG, msg="Checking for all the key: value pair from output")
        pattern = re.compile(
            r"(?P<property_name>[\S \f\t\v]+)\s+:\s(?P<property_value>[\S \f\t\v]*)(?P<property_value_add>(?:\s{3}.+)*)"
        )
        windows_dict = {}
        for match in pattern.finditer(block):
            windows_property = match.group("property_name").strip()
            windows_property_value = ""
            if match.group("property_value"):
                windows_property_value = match.group("property_value").rstrip()
            if match.group("property_value_add"):
                windows_property_value += "".join(match.group("property_value_add").split())
            windows_dict[windows_property] = windows_property_value
        return windows_dict

    def _get_multiline_registry_value(self, path: str, reg_key: str) -> str:
        """Get registry value of a registry key for REG_MULTI_SZ type.

        :param path: Path to Windows registry from which to take the properties
        :param reg_key: registry key
        :return: registry value in dictionary type string output (i.e.: {x, y, z})
        """
        abs_path = path.rstrip("\\")
        cmd = f"(get-itemproperty -path '{abs_path}').{reg_key}"
        output = self._connection.execute_powershell(cmd).stdout
        lines_to_str = ", ".join([_key.strip() for _key in output.strip().splitlines() if _key.strip() != ""])
        return f"{{{lines_to_str}}}"

    def get_registry_path(self, path: str, depth: int = 0) -> Dict:
        """Get values from Windows registry path.

        :param path: Path to Windows registry from which to take the properties
        :param depth: How deep go into sub-keys, be careful with big trees and large depth
        :return: Dictionary with property:value pairs or None on failure
        """
        abs_path = path.rstrip("\\")
        cmd = f"get-itemproperty -path '{abs_path}'"

        if depth > 0:
            logger.log(level=log_levels.MODULE_DEBUG, msg=f"\nCreating a command based on depth: {depth}")
            cmd = self._get_depth_command(cmd, abs_path, depth)

        output = self._connection.execute_powershell(cmd).stdout
        output = output.split("\n\n")
        logger.log(
            level=log_levels.MODULE_DEBUG,
            msg=f"\nSplitting hklm from {abs_path} as hklm is replaced by HKEY_LOCAL_MACHINE",
        )
        rpath = abs_path.split("\\", 1)[1]
        my_res = {}

        for block in output:
            if not block.strip():
                continue
            registry_dict = self._get_registry_dict(block)
            # if a registry value is a dict type and contains more data, it requires to get full data
            for reg_key in registry_dict:
                if registry_dict[reg_key].endswith("...}"):
                    logger.log(
                        level=log_levels.MODULE_DEBUG,
                        msg=f"Registry key {reg_key} contains more values than {registry_dict[reg_key]}.",
                    )
                    registry_dict[reg_key] = self._get_multiline_registry_value(path=path, reg_key=reg_key)
            ps_path = registry_dict["PSPath"].split(rpath)
            logger.log(
                level=log_levels.MODULE_DEBUG,
                msg=f"\nChecking if PS_Path contains additional value other than {rpath}",
            )
            if len(ps_path) > 1 and ps_path[1].strip():
                logger.log(level=log_levels.MODULE_DEBUG, msg=f"\nPS_Path contains additional depth {ps_path[1]}")
                for path in reversed(ps_path[1].split(r"\\")):
                    if path:
                        logger.log(level=log_levels.MODULE_DEBUG, msg=f"\nAssiging Additional depth values to {path}")
                        tmp_dict = {}
                        tmp_dict[path] = registry_dict
                        registry_dict = tmp_dict
            my_res = self._dict_merge(my_res, registry_dict)
        return my_res

    def get_feature_list(self, interface: str, cached: bool = True) -> Dict:
        """Get list of Adapter features in registry.

        :param interface: Interface Name for the adapter
        :param cached: to fetch from cached dict or from registry
        :return: Dictionary with property:value pairs or None on failure
        """
        driver_key = self._convert_interface_to_index(interface)
        if not (self._cached_feature_dict.get(interface) and cached):
            nic_idx = driver_key.rjust(4, "0")
            path = rf"{NIC_REGISTRY_BASE_PATH}\{nic_idx}"
            self._cached_feature_dict[interface] = self.get_registry_path(path)
        return self._cached_feature_dict[interface]

    def _convert_interface_to_index(self, interface_name: str) -> str:
        """Get the Interface Index from the given Interface Name.

        :param interface_name: Interface Name for the adapter
        :return: Interface index of the interface
        """
        cmd = "Get-CimInstance -ClassName Win32_NetworkAdapter | Select-Object -Property DeviceID, NetConnectionID"
        output = self._connection.execute_powershell(cmd).stdout
        interface_to_index_match = re.search(rf"(?P<index>\d+)\s+{interface_name}", output)
        if interface_to_index_match:
            return interface_to_index_match.group("index")
        raise WindowsRegistryException(f"Failed to get Interface Index from Interface: {interface_name}")

    def registry_exists(self, path: str) -> bool:
        """Check if registry path exists.

        :param path: Windows registry path to check that it exists
        :return: True if registry path exists; False it does not exist
        """
        cmd = rf'Test-Path -Path "{path}"'
        output = self._connection.execute_powershell(cmd, custom_exception=WindowsRegistryExecutionError).stdout.strip()
        return output.lower() == "true"

    def _add_remove_registry_key(self, interface: str, feature: str, value: str) -> None:
        """Set feature in registry.

        :param interface: Interface Name for the adapter
        :param feature: Feature name
        :param value: Value to set
        :raises WindowsRegistryException: if user provided value is not set for the feature/feature not present
        :raises WindowsRegistryExecutionError: if command execution fails
        """
        if feature in self.get_feature_list(interface):
            try:
                cmd = (
                    f"Set-NetAdapterAdvancedProperty -name '{interface}'"
                    f" -RegistryKeyword {feature} -RegistryValue {value}"
                )
                self._connection.execute_powershell(cmd, custom_exception=WindowsRegistryExecutionError)
                self.check_registry_key(interface, feature, value)
            except WindowsRegistryExecutionError as e:
                raise WindowsRegistryException("Failed to execute the command.") from e
        else:
            raise WindowsRegistryException(f"Feature {feature} not present in feature list")

    def add_registry_key(self, interface: str, feature: str, value: str) -> None:
        """Set feature to user value in registry.

        :param interface: Interface Name for the adapter
        :param feature: Feature name
        :param value: Value to set
        :raises WindowsRegistryException: if user provided value is not set for the feature/feature not present
        :raises WindowsRegistryExecutionError: if command execution fails
        """
        return self._add_remove_registry_key(interface, feature, value)

    def remove_registry_key(self, interface: str, feature: str) -> None:
        """Set the feature value to zero in registry.

        :param interface: Interface Name for the adapter
        :param feature: Feature name
        :raises WindowsRegistryException: if user provided value is not set for the feature/feature not present
        :raises WindowsRegistryExecutionError: if command execution fails
        """
        return self._add_remove_registry_key(interface, feature, value="0")

    def check_registry_key(self, interface: str, feature: str, value: str) -> None:
        """Check feature in registry.

        :param interface: Interface name for the adapter
        :param feature: Feature name
        :param value: Value to check
        :raises WindowsRegistryException: if user provided value is not set for the feature//feature not present
        :raises WindowsRegistryExecutionError: if command execution fails
        """
        if feature in self.get_feature_list(interface):
            try:
                cmd = f"Get-NetAdapterAdvancedProperty -name '{interface}' -RegistryKeyword {feature}"
                output = self._connection.execute_powershell(cmd, custom_exception=WindowsRegistryExecutionError).stdout
                match = re.search(r"{(?P<index>\d+)}", output)
                if not match:
                    raise WindowsRegistryException(f"Failed: Unable to find index in the output for {feature}.")

                if match.group("index") != value:
                    raise WindowsRegistryException(f"Failed: The value {value} is not set for {feature}.")

            except WindowsRegistryExecutionError as e:
                raise WindowsRegistryException(f"Failed to execute the command on interface {interface}") from e
        else:
            raise WindowsRegistryException(f"Feature {feature} not present in feature list")

    def _create_new_property(
        self, interface: str, feature: str, value: str, base_path: str, prop_type: PropertyType
    ) -> None:
        """Create a new feature in registry.

        :param interface: Interface name for the adapter
        :param feature: Feature name
        :param value: Value to set
        :param base_path: Specify an absolute path in registry. Default is for NIC settings.
        :param prop_type: Registry property type
        :raises WindowsRegistryException: if failed to create a new feature
        """
        logger.log(level=log_levels.MODULE_DEBUG, msg=f"Creating a new feature {feature}")
        cmd = f"new-itemproperty -path '{base_path}' -Name {feature} -Value {value}"
        if prop_type != PropertyType.NONE:
            cmd += f" -PropertyType {prop_type.value}"
        output = self._connection.execute_powershell(cmd, expected_return_codes={0, 1})
        if output.stderr:
            raise WindowsRegistryException(f"Error in creating the feature: {feature}")
        else:
            logger.log(
                level=log_levels.MODULE_DEBUG,
                msg=f"Updating the cached feature dict to include newly added feature: {feature}",
            )
            self._cached_feature_dict[interface] = self.get_registry_path(base_path)

    def set_feature(
        self,
        interface: str,
        feature: str,
        value: str,
        prop_type: PropertyType = PropertyType.NONE,
        base_path: str = None,
        new_prop_create: bool = True,
    ) -> None:
        """Set or create new feature in registry based on user path or base path.

        :param interface: Interface name for the adapter
        :param feature: Feature name
        :param value: Value to set
        :param prop_type: Registry property type
        :param base_path: Specify an absolute path in registry. Default is for NIC settings.
        :param new_prop_create: Specify whether the property should be created if the property is not found
        :raises WindowsRegistryException: if feature/feature not present and failed to execute the command
        """
        driver_key = self._convert_interface_to_index(interface)
        nic_idx = driver_key.rjust(4, "0")
        if not base_path:
            base_path = rf"{NIC_REGISTRY_BASE_PATH}\{nic_idx}"
            logger.log(level=log_levels.MODULE_DEBUG, msg=f"Registry Base Path: {base_path} considered")
            if not value:
                value = "''"
            elif prop_type == PropertyType.STRING:
                value = f"'{value}'"
        try:
            if feature in self.get_feature_list(interface):
                logger.log(level=log_levels.MODULE_DEBUG, msg=f"Value: {value} is set for feature: {feature}")
                cmd = f"set-itemproperty -path '{base_path}' -Name {feature} -Value {value}"
                self._connection.execute_powershell(cmd, expected_return_codes={0})
                self._cached_feature_dict[interface] = self.get_registry_path(base_path)
            elif new_prop_create:
                self._create_new_property(interface, feature, value, base_path, prop_type)
            else:
                raise WindowsRegistryException(
                    f"Feature: {feature} not present and new_prop_create flag is not set on {interface}"
                )
        except WindowsRegistryExecutionError as e:
            raise WindowsRegistryException(f"Failed to execute the command on interface {interface}") from e

    def remove_feature(self, interface: str, feature: str, base_path: str = None) -> None:
        """Remove feature entry from registry.

        :param interface: Interface name for the adapter
        :param feature: Feature name
        :param base_path: Specify an absolute path in registry. Default is for NIC settings.
        :raises WindowsRegistryException: if command execution error
        """
        driver_key = self._convert_interface_to_index(interface)
        nic_idx = driver_key.rjust(4, "0")

        if not base_path:
            base_path = rf"{NIC_REGISTRY_BASE_PATH}\{nic_idx}"
            logger.log(level=log_levels.MODULE_DEBUG, msg=f"Registry Base Path: {base_path} considered")
        cmd = f"remove-itemproperty -path '{base_path}' -name {feature}"
        try:
            output = self._connection.execute_powershell(cmd, expected_return_codes={0, 1})
            if output.stderr:
                raise WindowsRegistryException(f"Error while removing the feature: {feature} on {interface} adapter.")
            else:
                logger.log(
                    level=log_levels.MODULE_DEBUG, msg=f"Updating the cached feature dict to remove feature: {feature}"
                )
                self._cached_feature_dict[interface] = self.get_registry_path(base_path)
        except WindowsRegistryExecutionError as e:
            raise WindowsRegistryException(f"Failed to execute the command on interface {interface}") from e

    def get_feature_possible_values(self, interface: str, feature: str) -> List[int]:
        """Get list of feature's all supported values.

        :param interface: Interface name for the adapter
        :param feature: Feature name
        :return: Feature's all supported values
        """
        cmd = (
            f'Set-NetAdapterAdvancedProperty -Name "{interface}" -RegistryKeyword "{feature}"'
            ' -RegistryValue "-9999999"'
        )

        output = self._connection.execute_powershell(cmd, expected_return_codes={0, 1}).stderr
        match_range = re.search(r"Value must be within the range (?P<min_val>\d+) - (?P<max_val>\d+)", output)
        match_range_step = re.search(
            r"Value must be within the range (?P<min_val>\d+) - (?P<max_val>\d+), in increments of (?P<inc_val>\d+)",
            output,
        )
        if match_range_step or match_range:
            match = match_range_step if match_range_step else match_range
            return list(
                range(
                    int(match.group("min_val")),
                    int(match.group("max_val")) + 1,
                    1 if len(match.groups()) == 2 else int(match.group("inc_val")),
                )
            )
        else:
            logger.log(
                level=log_levels.MODULE_DEBUG,
                msg=f"Match Range or Match Step range didn't match for feature: {feature}",
            )
            cmd = (
                f'(Get-NetAdapterAdvancedProperty -Name "{interface}" -RegistryKeyword "{feature}")'
                ".ValidRegistryValues"
            )
            logger.log(
                level=log_levels.MODULE_DEBUG, msg=f"\nTrying to get the valid registry values for feature: {feature}"
            )
            output = self._connection.execute_powershell(cmd, expected_return_codes={0}).stdout
            try:
                return [int(x) for x in output.splitlines()]
            except ValueError:
                logger.log(level=log_levels.MODULE_DEBUG, msg="No output could be parsed")
        return []

    def get_registry_childitems(self, path: str, depth: int = 0) -> Dict[str, Dict[str, str]]:
        """Get child items from Windows registry path.

        :param path: Path to Windows registry from which to get the properties
        :param depth: How deep go into subways, be careful with big trees and large depth
        :return: ChildItems's property:value pairs
        """
        cmd = f"get-childitem -path '{path}' | select Name"
        output = self._connection.execute_powershell(cmd).stdout
        retval = {}
        for child_name in output.splitlines():
            if "\\" in child_name:
                basic_path = path.split("\\", 1)[0]
                child_name_path = child_name.strip().split("\\", 1)[1]
                child_path = f"{basic_path}\\{child_name_path}"
                retval[child_path] = self.get_registry_path(child_path, depth)
        return retval

    def check_proset_registry(self) -> bool:
        """Check PROSET entries exist in registry.

        :return: True if entries present, False otherwise
        """
        items = self.get_registry_childitems(PROSET_PATH)
        if not items:
            logger.log(level=log_levels.MODULE_DEBUG, msg=f"Could not find subpaths in: {PROSET_PATH}")
            return False

        key_names = [key.split("\\")[-1] for key in items]
        key_counter = 0
        for key in PROSET_KEY_LIST:
            if key not in key_names:
                logger.log(level=log_levels.MODULE_DEBUG, msg=f"No key {key} in the path: {PROSET_PATH}")
            else:
                logger.log(level=log_levels.MODULE_DEBUG, msg=f"{key} key found in the path: {PROSET_PATH}")
                key_counter += 1
        return key_counter == len(PROSET_KEY_LIST)

    def remove_registry_subkeys(self, path: str) -> None:
        """Remove all registry sub-keys from given path.

        :param path: Path to Windows registry to remove
        :raises WindowsRegistryException: if path doesn't exist or failed to remove items.
        """
        if not self.registry_exists(path):
            raise WindowsRegistryException(f"Registry Path: {path} does not exist.")

        cmd = rf'Remove-Item -Path "{path}" -Recurse'
        output = self._connection.execute_powershell(
            cmd, expected_return_codes={0, 1}, custom_exception=WindowsRegistryExecutionError
        )
        if output.stderr:
            raise WindowsRegistryException(f"Error while removing the registry subkeys from path: {path}")

    def _get_saved_params_path(self, interface: str) -> Union[str, None]:
        """Get path to saved params file.

        :param interface: Interface Name for the adapter
        :return: "Params", "savedParams", None
        """
        driver_key = self._convert_interface_to_index(interface)
        nic_idx = driver_key.rjust(4, "0")
        # check if part path is known
        if self._cached_saved_params_path:
            return self._cached_saved_params_path

        cmd = rf"dir '{NIC_REGISTRY_BASE_PATH}\{nic_idx}\Ndi\*'| Format-List -Property PSChildName"
        output = self._connection.execute_powershell(cmd, custom_exception=WindowsRegistryExecutionError).stdout

        if ": savedParams" in output:
            self._cached_saved_params_path = "savedParams"
            return "savedParams"
        elif ": params" in output.casefold():
            self._cached_saved_params_path = "Params"
            return "Params"
        else:
            logger.log(level=log_levels.MODULE_DEBUG, msg=f"Cannot find 'savedParams' nor 'Params' directory: {output}")
            return None

    def _get_feature_attribute(self, interface: str, feature: str, attribute_name: str) -> Union[str, int]:
        """Get a feature from a custom tree in registry.

        :param interface: Interface Name for the adapter
        :param feature: Feature name
        :param attribute_name: name of key
        :return: Attribute value
        :raises WindowsRegistryException: if feature or attribute doesn't exist.
        """
        driver_key = self._convert_interface_to_index(interface)
        if not self._cached_feature_attributes:
            nic_idx = driver_key.rjust(4, "0")
            part_path = self._get_saved_params_path(interface)
            cmd = rf"get-itemproperty -path '{NIC_REGISTRY_BASE_PATH}\{nic_idx}\Ndi\{part_path}\*'"
            output = self._connection.execute_powershell(cmd, custom_exception=WindowsRegistryExecutionError).stdout
            features = parse_powershell_list(output)
            for feat in features:
                self._cached_feature_attributes[feat["PSChildName"]] = feat

        if feature not in self._cached_feature_attributes.keys():
            raise WindowsRegistryException(f"Cannot find the {feature} feature on {interface} adapter")
        if attribute_name in self._cached_feature_attributes[feature].keys():
            return self._cached_feature_attributes[feature][attribute_name]
        else:
            raise WindowsRegistryException(
                f"Cannot find attributes {attribute_name} for {feature} feature on {interface} adapter"
            )

    def _get_buffers(self, interface: str, buffers: str, attr: BuffersAttribute) -> int:
        """Get buffers value on the given interface buffers.

        :param attr: Buffers attribute.
        :return: Buffers size for the adapter or error
        """
        if attr.value == "None":
            output = self.get_feature_list(interface)[buffers]
        else:
            output = self._get_feature_attribute(interface, buffers, attr.value)
        return int(output)

    def get_rx_buffers(self, interface: str, attr: BuffersAttribute = BuffersAttribute.NONE) -> int:
        """Get RX buffers value on the given interface.

        :param interface: Name of the adapter
        :param attr: RX buffers attribute.
        :return: RX buffers size for the adapter or error
        """
        return self._get_buffers(interface, "*ReceiveBuffers", attr)

    def get_tx_buffers(self, interface: str, attr: BuffersAttribute = BuffersAttribute.NONE) -> int:
        """Get TX buffers size on the given interface.

        :param interface: Name of the adapter
        :param attr: TX buffers attribute.
        :return: TX buffers size for the adapter, or error
        """
        return self._get_buffers(interface, "*TransmitBuffers", attr)

    def get_feature_enum(self, interface: str, feature: str) -> Union[Dict[str, str]]:
        """Get enum dictionary for feature.

        :param interface: Name of the adapter
        :param feature: Feature name
        :return: feature enum key value pairs
        :raises WindowsRegistryException: if feature doesn't exist
        """
        driver_key = self._convert_interface_to_index(interface)
        if feature in self.get_feature_list(interface):
            nic_idx = driver_key.rjust(4, "0")
            part_path = self._get_saved_params_path(interface)
            cmd = rf"get-itemproperty -path '{NIC_REGISTRY_BASE_PATH}\{nic_idx}\Ndi\{part_path}\{feature}\*'"
            output = self._connection.execute_powershell(cmd, custom_exception=WindowsRegistryExecutionError).stdout
            items = parse_powershell_list(output)
            return items[0]
        else:
            raise WindowsRegistryException(f"Feature {feature} not present on interface: {interface}")

    def set_itemproperty(self, path: str, name: str, value: str) -> None:
        """Set itemproperty for feature.

        :param path: path for the registry
        :param name: feature to set
        :param value: value to set
        """
        cmd = f"set-itemproperty -path '{path}' -Name {name} -Value {value}"
        self._connection.execute_powershell(cmd, expected_return_codes=[0])
