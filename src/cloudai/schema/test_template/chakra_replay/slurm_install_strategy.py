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

from cloudai.schema.system.slurm.strategy import SlurmInstallStrategy


class ChakraReplaySlurmInstallStrategy(SlurmInstallStrategy):
    """Installation strategy for CommsTraceReplay on Slurm systems."""

    def is_installed(self) -> bool:
        return True

    def install(self) -> None:
        if not self.is_installed():
            return

    def uninstall(self) -> None:
        return
