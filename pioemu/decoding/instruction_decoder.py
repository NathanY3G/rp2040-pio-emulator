# Copyright 2025 Nathan Young
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from pioemu.instruction import JmpInstruction

# TODO - Add documentation


class InstructionDecoder:
    def __init__(self, side_set_count: int = 0):
        self.side_set_count = side_set_count
        self.bits_for_delay = 5 - self.side_set_count
        self.delay_mask = (1 << self.bits_for_delay) - 1

    def decode(self, opcode: int) -> JmpInstruction | None:
        target_address = opcode & 0x1F
        condition = (opcode >> 5) & 7

        delay = (opcode >> 8) & self.delay_mask
        side_set = opcode >> 8 + self.bits_for_delay

        return JmpInstruction(target_address, condition, delay, side_set)
