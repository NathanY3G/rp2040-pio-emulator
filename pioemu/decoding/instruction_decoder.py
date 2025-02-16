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


class InstructionDecoder:
    """
    Decodes state-machine opcodes into higher-level representations.
    """

    def __init__(self, side_set_count: int = 0):
        """
        Parameters
        ----------
        side_set_count (int): Number of bits of side-set information encoded into opcodes.
        """
        self.side_set_count = side_set_count
        self.bits_for_delay = 5 - self.side_set_count
        self.delay_mask = (1 << self.bits_for_delay) - 1

    def decode(self, opcode: int) -> JmpInstruction | None:
        """
        Decodes an opcode into an object representing the instruction and its parameters.

        Parameters:
        opcode (int): The opcode to decode.

        Returns:
        Instruction: Representation of the given opcode or None when invalid/not supported
        """

        if (opcode >> 13) & 7 == 0:
            return self._decode_jmp(opcode)

        return None

    def _decode_jmp(self, opcode: int) -> JmpInstruction:
        target_address = opcode & 0x1F
        condition = (opcode >> 5) & 7

        delay_cycles = (opcode >> 8) & self.delay_mask
        side_set_value = opcode >> 8 + self.bits_for_delay

        return JmpInstruction(
            opcode, target_address, condition, delay_cycles, side_set_value
        )
