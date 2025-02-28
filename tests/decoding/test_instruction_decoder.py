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
from pioemu.instruction import (
    InInstruction,
    JmpInstruction,
    OutInstruction,
    PullInstruction,
    PushInstruction,
)
from tests.opcodes import Opcodes


# TODO: Add invalid opcodes for PULL and PUSH
@pytest.mark.parametrize("opcode", [Opcodes.nop(), 0x4081, 0x40A1])
def test_none_returned_for_unsupported_opcodes(opcode: int):
    decoded_instruction = InstructionDecoder().decode(opcode)

    assert decoded_instruction is None


@pytest.mark.parametrize(
    "opcode, side_set_count, expected_source, expected_bit_count, expected_delay_cycles, expected_side_set_value",
    [
        pytest.param(0x5C01, 0, 0, 1, 28, 0, id="in pins, 1 [28]"),
        pytest.param(0x5B21, 0, 1, 1, 27, 0, id="in x, 1 [27]"),
        pytest.param(0x4F41, 3, 2, 1, 3, 3, id="in y, 1 side 0b011 [3]"),
        pytest.param(0x5C61, 4, 3, 1, 0, 14, id="in null, 1 side 0b1110"),
        pytest.param(0x50C1, 1, 6, 1, 0, 1, id="in isr, 1 side 0b1"),
        pytest.param(0x42E1, 5, 7, 1, 0, 2, id="in osr, 1 side 0b00010"),
        pytest.param(0x5AE0, 4, 7, 32, 0, 13, id="in osr, 32 side 0b1101"),
        pytest.param(0x4DC0, 2, 6, 32, 5, 1, id="in isr, 32 side 0b01 [5]"),
        pytest.param(0x5060, 2, 3, 32, 0, 2, id="in null, 32 side 0b10"),
        pytest.param(0x5340, 3, 2, 32, 3, 4, id="in y, 32 side 0b100 [3]"),
        pytest.param(0x4820, 2, 1, 32, 0, 1, id="in x, 32 side 0b01"),
        pytest.param(0x4D00, 5, 0, 32, 0, 13, id="in pins, 32 side 0b01101"),
    ],
)
def test_decoding_of_in_instruction(
    opcode: int,
    side_set_count: int,
    expected_source: int,
    expected_bit_count: int,
    expected_delay_cycles: int,
    expected_side_set_value: int,
):
    instruction_decoder = InstructionDecoder(side_set_count)

    decoded_instruction = instruction_decoder.decode(opcode)

    assert decoded_instruction == InInstruction(
        opcode=opcode,
        source=expected_source,
        bit_count=expected_bit_count,
        delay_cycles=expected_delay_cycles,
        side_set_value=expected_side_set_value,
    )


@pytest.mark.parametrize(
    "opcode, side_set_count, expected_target_address, expected_condition, expected_delay_cycles, expected_side_set_value",
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
    expected_delay_cycles: int,
    expected_side_set_value: int,
):
    instruction_decoder = InstructionDecoder(side_set_count)

    decoded_instruction = instruction_decoder.decode(opcode)

    assert decoded_instruction == JmpInstruction(
        opcode=opcode,
        target_address=expected_target_address,
        condition=expected_condition,
        delay_cycles=expected_delay_cycles,
        side_set_value=expected_side_set_value,
    )


@pytest.mark.parametrize(
    "opcode, side_set_count, expected_destination, expected_bit_count, expected_delay_cycles, expected_side_set_value",
    [
        pytest.param(0x6901, 4, 0, 1, 1, 4, id="out pins, 1 side 0b0100 [1]"),
        pytest.param(0x6D21, 5, 1, 1, 0, 13, id="out x, 1 side 0b01101"),
        pytest.param(0x6041, 4, 2, 1, 0, 0, id="out y, 1 side 0b0000"),
        pytest.param(0x7661, 0, 3, 1, 22, 0, id="out null, 1 [22]"),
        pytest.param(0x6C81, 3, 4, 1, 0, 3, id="out pindirs, 1 side 0b011"),
        pytest.param(0x7AA1, 4, 5, 1, 0, 13, id="out pc, 1 side 0b1101"),
        pytest.param(0x6FC1, 1, 6, 1, 15, 0, id="out isr, 1 side 0b0 [15]"),
        pytest.param(0x60E1, 4, 7, 1, 0, 0, id="out exec, 1 side 0b0000"),
        pytest.param(0x76E0, 0, 7, 32, 22, 0, id="out exec, 32 [22]"),
        pytest.param(0x7DC0, 5, 6, 32, 0, 29, id="out isr, 32 side 0b11101"),
        pytest.param(0x73A0, 4, 5, 32, 1, 9, id="out pc, 32 side 0b1001 [1]"),
        pytest.param(0x7480, 2, 4, 32, 4, 2, id="out pindirs, 32 side 0b10 [4]"),
        pytest.param(0x6B60, 4, 3, 32, 1, 5, id="out null, 32 side 0b0101 [1]"),
        pytest.param(0x7440, 4, 2, 32, 0, 10, id="out y, 32 side 0b1010"),
        pytest.param(0x6920, 5, 1, 32, 0, 9, id="out x, 32 side 0b01001"),
        pytest.param(0x6900, 1, 0, 32, 9, 0, id="out pins, 32 side 0b0 [9]"),
    ],
)
def test_decoding_of_out_instruction(
    opcode: int,
    side_set_count: int,
    expected_destination: int,
    expected_bit_count: int,
    expected_delay_cycles: int,
    expected_side_set_value: int,
):
    instruction_decoder = InstructionDecoder(side_set_count)

    decoded_instruction = instruction_decoder.decode(opcode)

    assert decoded_instruction == OutInstruction(
        opcode=opcode,
        destination=expected_destination,
        bit_count=expected_bit_count,
        delay_cycles=expected_delay_cycles,
        side_set_value=expected_side_set_value,
    )


# fmt: off
@pytest.mark.parametrize(
    "opcode, side_set_count, expected_if_empty_flag, expected_block_flag, expected_delay_cycles, expected_side_set_value",
    [
        pytest.param(0x9080, 5, False, False, 0, 16, id="pull noblock side 0b10000"),
        pytest.param(0x86C0, 3, True, False, 2, 1, id="pull ifempty noblock side 0b001 [2]"),
        pytest.param(0x8BE0, 5, True, True, 0, 11, id="pull ifempty block side 0b01011"),
        pytest.param(0x9FA0, 1, False, True, 15, 1, id="pull block side 0b1 [15]"),
    ],
)
# fmt: on
def test_decoding_of_pull_instruction(
    opcode: int,
    side_set_count: int,
    expected_if_empty_flag: int,
    expected_block_flag: int,
    expected_delay_cycles: int,
    expected_side_set_value: int,
):
    instruction_decoder = InstructionDecoder(side_set_count)

    decoded_instruction = instruction_decoder.decode(opcode)

    assert decoded_instruction == PullInstruction(
        opcode=opcode,
        if_empty=expected_if_empty_flag,
        block=expected_block_flag,
        delay_cycles=expected_delay_cycles,
        side_set_value=expected_side_set_value,
    )


# fmt: off
@pytest.mark.parametrize(
    "opcode, side_set_count, expected_if_full_flag, expected_block_flag, expected_delay_cycles, expected_side_set_value",
    [
        pytest.param(0x8600, 1, False, False, 6, 0, id="push noblock side 0b0 [6]"),
        pytest.param(0x9340, 5, True, False, 0, 19, id="push iffull noblock side 0b10011"),
        pytest.param(0x9960, 4, True, True, 1, 12, id="push iffull block side 0b1100 [1]"),
        pytest.param(0x8B20, 0, False, True, 11, 0, id="push block [11]"),
    ],
)
# fmt: on
def test_decoding_of_push_instruction(
    opcode: int,
    side_set_count: int,
    expected_if_full_flag: int,
    expected_block_flag: int,
    expected_delay_cycles: int,
    expected_side_set_value: int,
):
    instruction_decoder = InstructionDecoder(side_set_count)

    decoded_instruction = instruction_decoder.decode(opcode)

    assert decoded_instruction == PushInstruction(
        opcode=opcode,
        if_full=expected_if_full_flag,
        block=expected_block_flag,
        delay_cycles=expected_delay_cycles,
        side_set_value=expected_side_set_value,
    )
