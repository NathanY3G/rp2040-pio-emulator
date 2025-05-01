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
from typing import Optional
from pioemu.instruction import (
    InInstruction,
    Instruction,
    JmpInstruction,
    OutInstruction,
)


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
        self.delay_cycles_mask = (1 << self.bits_for_delay) - 1

    def decode(self, opcode: int) -> Optional[Instruction]:
        """
        Decodes an opcode into an object representing the instruction and its parameters.

        Parameters:
        opcode (int): The opcode to decode.

        Returns:
        Instruction: Representation of the given opcode or None when invalid/not supported
        """

        match (opcode >> 13) & 7:
            case 0:
                return self._decode_jmp(opcode)
            case 2:
                return self._decode_in(opcode)
            case 3:
                return self._decode_out(opcode)
            case _:
                return None

    def _decode_in(self, opcode: int) -> InInstruction | None:
        bit_count = opcode & 0x1F
        if bit_count == 0:
            bit_count = 32

        source = (opcode >> 5) & 7

        # Check if source has been reserved for future use
        if source == 4 or source == 5:
            return None

        delay_cycles, side_set_value = self._extract_delay_cycles_and_side_set(opcode)

        return InInstruction(
            opcode=opcode,
            source=source,
            bit_count=bit_count,
            delay_cycles=delay_cycles,
            side_set_value=side_set_value,
        )

    def _decode_jmp(self, opcode: int) -> JmpInstruction:
        delay_cycles, side_set_value = self._extract_delay_cycles_and_side_set(opcode)

        return JmpInstruction(
            opcode=opcode,
            target_address=opcode & 0x1F,
            condition=(opcode >> 5) & 7,
            delay_cycles=delay_cycles,
            side_set_value=side_set_value,
        )

    def _decode_out(self, opcode: int) -> OutInstruction:
        bit_count = opcode & 0x1F
        if bit_count == 0:
            bit_count = 32

        delay_cycles, side_set_value = self._extract_delay_cycles_and_side_set(opcode)

        return OutInstruction(
            opcode=opcode,
            destination=(opcode >> 5) & 7,
            bit_count=bit_count,
            delay_cycles=delay_cycles,
            side_set_value=side_set_value,
        )

    def _extract_delay_cycles_and_side_set(self, opcode: int):
        delay_cycles_and_side_set = (opcode >> 8) & 0x1F
        delay_cycles = delay_cycles_and_side_set & self.delay_cycles_mask
        side_set_value = delay_cycles_and_side_set >> self.bits_for_delay

        return (delay_cycles, side_set_value)
