# Copyright 2021 Nathan Young
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
from functools import partial, wraps
from .conditions import (
    always,
    gpio_low,
    gpio_high,
    transmit_fifo_not_empty,
    x_register_equals_zero,
    x_register_not_equal_to_y_register,
    x_register_not_equal_to_zero,
    y_register_equals_zero,
    y_register_not_equal_to_zero,
)
from .instruction import Instruction
from .instructions import (
    out_null,
    out_pindirs,
    out_pins,
    out_x,
    out_y,
    pull_blocking,
    pull_nonblocking,
)
from .primitive_operations import (
    copy_data_to_isr,
    copy_data_to_osr,
    copy_data_to_pin_directions,
    copy_data_to_pins,
    copy_data_to_program_counter,
    copy_data_to_x,
    copy_data_to_y,
)


class InstructionDecoder:
    """
    Decodes opcodes representing instructions into callables that emulate those
    instructions.
    """

    def __init__(self, shifter_for_osr):
        """
        Parameters:
        shifter_for_osr (Callable[[ShiftRegister, int], (ShiftRegister, int)]): Used for shifting the contents of the OSR.
        """

        self.lookup_table = self._build_lookup_table(shifter_for_osr)

    def decode(self, opcode):
        """
        Decodes the given opcode and returns a callable which emulates it.

        Parameters:
        opcode (int): The opcode to decode.

        Returns:
        Instruction: Representation of the instruction or None.
        """

        instruction = opcode >> 13

        if instruction == 1:  # WAIT
            return self._decode_wait(opcode)
        else:
            return self.lookup_table.get(opcode & 0xE0E0, None)

    def _decode_wait(self, opcode):
        index = opcode & 0x001F

        if opcode & 0x0080:
            condition = partial(gpio_high, index)
        else:
            condition = partial(gpio_low, index)

        return Instruction(condition, lambda data, state: state)

    def _build_lookup_table(self, shifter_for_osr):
        return {
            0x0000: Instruction(always, copy_data_to_program_counter),
            0x0020: Instruction(x_register_equals_zero, copy_data_to_program_counter),
            0x0040: Instruction(
                x_register_not_equal_to_zero, copy_data_to_program_counter
            ),
            0x0060: Instruction(y_register_equals_zero, copy_data_to_program_counter),
            0x0080: Instruction(
                y_register_not_equal_to_zero, copy_data_to_program_counter
            ),
            0x00A0: Instruction(
                x_register_not_equal_to_y_register, copy_data_to_program_counter
            ),
            0x6000: Instruction(
                always,
                self._normalize_bit_count(partial(out_pins, shifter_for_osr)),
            ),
            0x6020: Instruction(
                always,
                self._normalize_bit_count(partial(out_x, shifter_for_osr)),
            ),
            0x6040: Instruction(
                always,
                self._normalize_bit_count(partial(out_y, shifter_for_osr)),
            ),
            0x6060: Instruction(
                always,
                self._normalize_bit_count(partial(out_null, shifter_for_osr)),
            ),
            0x6080: Instruction(
                always,
                self._normalize_bit_count(partial(out_pindirs, shifter_for_osr)),
            ),
            0x8080: Instruction(always, pull_nonblocking),
            0x80A0: Instruction(transmit_fifo_not_empty, pull_blocking),
            0xA000: Instruction(always, copy_data_to_pins),
            0xA020: Instruction(always, copy_data_to_x),
            0xA040: Instruction(always, copy_data_to_y),
            0xA0C0: Instruction(always, copy_data_to_isr),
            0xA0E0: Instruction(always, copy_data_to_osr),
            0xE000: Instruction(always, copy_data_to_pins),
            0xE020: Instruction(always, copy_data_to_x),
            0xE040: Instruction(always, copy_data_to_y),
            0xE080: Instruction(always, copy_data_to_pin_directions),
        }

    def _normalize_bit_count(self, function):
        @wraps(function)
        def wrapper(bit_count, state):
            if bit_count == 0:
                return function(32, state)
            else:
                return function(bit_count, state)

        return wrapper
