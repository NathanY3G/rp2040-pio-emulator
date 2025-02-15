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
import pytest
from pioemu.decoding.instruction_decoder import InstructionDecoder
from pioemu.instruction import JmpInstruction


@pytest.mark.parametrize(
    "opcode, side_set_count, expected_target_address, expected_condition, expected_delay, expected_side_set",
    [
        pytest.param(0x1A20, 3, 0, 1, 2, 6, id="jmp !x 0 side 0b110 [2]"),
        pytest.param(0x1440, 2, 0, 2, 4, 2, id="jmp x-- 0 side 0b10 [4]"),
        pytest.param(0x0560, 0, 0, 3, 5, 0, id="jmp !y 0 [5]"),
        pytest.param(0x1680, 1, 0, 4, 6, 1, id="jmp y-- 0 side 0b1 [6]"),
        pytest.param(0x15A0, 3, 0, 5, 1, 5, id="jmp x!=y 0 side 0b101 [1]"),
        pytest.param(0x18C0, 2, 0, 6, 0, 3, id="jmp pin 0 side 0b11"),
        pytest.param(0x13E0, 4, 0, 7, 1, 9, id="jmp !osre 0 side 0b1001 [1]"),
        pytest.param(0x11FF, 5, 31, 7, 0, 17, id="jmp !osre 31 side 0b10001"),
        pytest.param(0x19DF, 2, 31, 6, 1, 3, id="jmp pin 31 side 0b11 [1]"),
        pytest.param(0x17BF, 2, 31, 5, 7, 2, id="jmp x!=y 31 side 0b10 [7]"),
        pytest.param(0x109F, 1, 31, 4, 0, 1, id="jmp y-- 31 side 0b1"),
        pytest.param(0x077F, 1, 31, 3, 7, 0, id="jmp !y 31 side 0b0 [7]"),
        pytest.param(0x005F, 1, 31, 2, 0, 0, id="jmp x-- 31 side 0b0"),
        pytest.param(0x0B3F, 0, 31, 1, 11, 0, id="jmp !x 31 [11]"),
        pytest.param(0x1D1F, 4, 31, 0, 1, 14, id="jmp 31 side 0b1110 [1]"),
    ],
)
def test_decoding_of_jmp_instruction(
    opcode: int,
    side_set_count: int,
    expected_target_address: int,
    expected_condition: int,
    expected_delay: int,
    expected_side_set: int,
):
    instruction_decoder = InstructionDecoder(side_set_count)
    instruction = instruction_decoder.decode(opcode)

    assert isinstance(instruction, JmpInstruction)

    assert instruction.target_address == expected_target_address
    assert instruction.condition == expected_condition
    assert instruction.delay == expected_delay
    assert instruction.side_set == expected_side_set
