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
    x_register_equals_zero,
    x_register_not_equal_to_y_register,
    y_register_equals_zero,
)
from .instructions import (
    jmp,
    jmp_when_x_is_non_zero_and_post_decrement,
    jmp_when_y_is_non_zero_and_post_decrement,
    next_instruction,
    out_null,
    out_pindirs,
    out_pins,
    out_x,
    out_y,
    pull_blocking,
    pull_nonblocking,
    wait_for_gpio_low,
    wait_for_gpio_high,
)
from .primitive_operations import (
    copy_data_to_isr,
    copy_data_to_osr,
    copy_data_to_pin_directions,
    copy_data_to_pins,
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
        Callable[[int, State], State]: Emulates the instruction when invoked.
        """

        return self.lookup_table.get(opcode & 0xE0E0, None)

    def _build_lookup_table(self, shifter_for_osr):
        return {
            0x0000: partial(jmp, lambda state: True),
            0x0020: partial(jmp, x_register_equals_zero),
            0x0040: jmp_when_x_is_non_zero_and_post_decrement,
            0x0060: partial(jmp, y_register_equals_zero),
            0x0080: jmp_when_y_is_non_zero_and_post_decrement,
            0x00A0: partial(jmp, x_register_not_equal_to_y_register),
            0x2020: wait_for_gpio_low,
            0x2080: wait_for_gpio_high,
            0x6000: self._normalize_bit_count(partial(out_pins, shifter_for_osr)),
            0x6020: self._normalize_bit_count(partial(out_x, shifter_for_osr)),
            0x6040: self._normalize_bit_count(partial(out_y, shifter_for_osr)),
            0x6060: self._normalize_bit_count(partial(out_null, shifter_for_osr)),
            0x6080: self._normalize_bit_count(partial(out_pindirs, shifter_for_osr)),
            0x8080: pull_nonblocking,
            0x80A0: pull_blocking,
            0xA000: lambda data, state: next_instruction(
                copy_data_to_pins(data, state)
            ),
            0xA020: lambda data, state: next_instruction(copy_data_to_x(data, state)),
            0xA040: lambda data, state: next_instruction(copy_data_to_y(data, state)),
            0xA0C0: lambda data, state: next_instruction(copy_data_to_isr(data, state)),
            0xA0E0: lambda data, state: next_instruction(copy_data_to_osr(data, state)),
            0xE000: lambda data, state: next_instruction(
                copy_data_to_pins(data, state)
            ),
            0xE020: lambda data, state: next_instruction(copy_data_to_x(data, state)),
            0xE040: lambda data, state: next_instruction(copy_data_to_y(data, state)),
            0xE080: lambda data, state: next_instruction(
                copy_data_to_pin_directions(data, state)
            ),
        }

    def _normalize_bit_count(self, function):
        @wraps(function)
        def wrapper(bit_count, state):
            if bit_count == 0:
                return function(32, state)
            else:
                return function(bit_count, state)

        return wrapper
