# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any, Dict, List, Set

from cloudai.schema.core.test import Test
from cloudai.schema.core.test_template import TestTemplate

from .base_multi_file_parser import BaseMultiFileParser


class TestParser(BaseMultiFileParser):
    """
    Parser for Test objects.

    Attributes
        test_template_mapping (Dict[str, TestTemplate]): Mapping of test template
            names to TestTemplate objects.
    """

    __test__ = False

    def __init__(
        self,
        directory_path: str,
        test_template_mapping: Dict[str, TestTemplate],
    ) -> None:
        """
        Initialize the TestParser instance.

        Args:
            directory_path (str): Path to the directory containing test data.
            test_template_mapping (Dict[str, TestTemplate]): Mapping of test
                template names to TestTemplate objects.
        """
        super().__init__(directory_path)
        self.test_template_mapping: Dict[str, TestTemplate] = test_template_mapping

    def _parse_data(self, data: Dict[str, Any]) -> Test:
        """
        Parse data for a Test object.

        Args:
            data (Dict[str, Any]): Data from a source (e.g., a TOML file).

        Returns:
            Test: Parsed Test object.
        """
        test_template_name = data.get("test_template_name", "")
        test_template = self.test_template_mapping.get(test_template_name)

        if not test_template:
            raise ValueError(f"TestTemplate with name '{test_template_name}' not found.")

        env_vars = data.get("env_vars", {})
        cmd_args = data.get("cmd_args", {})
        extra_env_vars = data.get("extra_env_vars", {})
        extra_cmd_args = data.get("extra_cmd_args", "")

        flattened_template_cmd_args = self._flatten_template_dict_keys(test_template.cmd_args)
        self._validate_args(cmd_args, flattened_template_cmd_args)

        flattened_template_env_vars = self._flatten_template_dict_keys(test_template.env_vars)
        self._validate_args(env_vars, flattened_template_env_vars)

        return Test(
            name=data.get("name", ""),
            description=data.get("description", ""),
            test_template=test_template,
            env_vars=env_vars,
            cmd_args=cmd_args,
            extra_env_vars=extra_env_vars,
            extra_cmd_args=extra_cmd_args,
        )

    def _parse_cmd_args(self, cmd_args_str: str) -> List[str]:
        """
        Parse a string of command-line arguments into a list.

        Args:
            cmd_args_str (str): Command-line arguments as a single string.

        Returns:
            List[str]: List of command-line arguments.
        """
        return cmd_args_str.split() if cmd_args_str else []

    def _flatten_template_dict_keys(self, nested_args: Dict[str, Any], parent_key: str = "") -> Set[str]:
        """
        Recursively flattens the nested dictionary structure from the test template.

        Includes keys with 'default' and 'values' as valid keys, while ignoring
        keys that specifically end with 'default' or 'values'.

        Args:
            nested_args (Dict[str, Any]): Nested argument structure from the test
                                          template.
            parent_key (str): Parent key for nested arguments.

        Returns:
            Set[str]: Set of all valid argument keys.
        """
        keys = set()
        for k, v in nested_args.items():
            new_key = f"{parent_key}.{k}" if parent_key else k

            if k in ["type", "values", "default"]:
                continue

            if isinstance(v, dict):
                if "default" in v:
                    keys.add(new_key)
                keys.update(self._flatten_template_dict_keys(v, new_key))
            else:
                keys.add(new_key)

        return keys

    def _validate_args(self, args: Dict[str, Any], valid_keys: Set[str]) -> None:
        """
        Validate the provided arguments against a set of valid keys.

        Args:
            args (Dict[str, Any]): Arguments provided in the TOML configuration.
            valid_keys (Set[str]): Set of valid keys from the flattened template
                                   arguments.

        Raises:
            ValueError: If an argument is not defined in the TestTemplate's arguments.
        """
        for arg_key in args:
            if arg_key not in valid_keys:
                raise ValueError(f"Argument '{arg_key}' is not defined in the TestTemplate's arguments.")
