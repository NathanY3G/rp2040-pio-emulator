# Copyright 2021, 2022, 2023 Nathan Young
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
from functools import partial
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
    output_shift_register_not_empty,
)
from .instruction import Instruction, ProgramCounterAdvance
from .instructions import (
    pull_blocking,
    pull_nonblocking,
)
from .primitive_operations import (
    read_from_isr,
    shift_into_isr,
    read_from_osr,
    shift_from_osr,
    read_from_pins,
    read_from_x,
    read_from_y,
    supplies_value,
    write_to_isr,
    write_to_osr,
    write_to_pin_directions,
    write_to_pins,
    write_to_program_counter,
    write_to_x,
    write_to_y,
    write_to_null,
)


class InstructionDecoder:
    """
    Decodes opcodes representing instructions into callables that emulate those
    instructions.
    """

    def __init__(self, shift_isr_method, shift_osr_method, jmp_pin):
        """
        Parameters
        ----------
        isr_shift_method : Callable[[ShiftRegister, int], (ShiftRegister, int)]
            Method to use to shift the contents of the Input Shift Register.
        osr_shift_method : Callable[[ShiftRegister, int], (ShiftRegister, int)]
            Method to use to shift the contents of the Output Shift Register.
        jmp_pin : int
            Pin that determines the branch taken by JMP PIN instructions.
        """

        self.shift_isr_method = shift_isr_method
        self.shift_osr_method = shift_osr_method

        self.decoding_functions = [
            self._decode_jmp,
            self._decode_wait,
            self._decode_in,
            self._decode_out,
            self._decode_pull,
            self._decode_mov,
            lambda _: None,
            self._decode_set,
        ]

        self.jmp_conditions = [
            always,
            x_register_equals_zero,
            x_register_not_equal_to_zero,
            y_register_equals_zero,
            y_register_not_equal_to_zero,
            x_register_not_equal_to_y_register,
            partial(gpio_high, jmp_pin),
            output_shift_register_not_empty,
        ]

        self.in_sources = [
            read_from_pins,
            read_from_x,
            read_from_y,
            supplies_value(0),
            None,
            None,
            read_from_isr,
            read_from_osr,
        ]

        self.mov_sources = [
            read_from_pins,
            read_from_x,
            read_from_y,
            supplies_value(0),
            None,
            None,
            read_from_isr,
            read_from_osr,
        ]

        self.mov_destinations = [
            write_to_pins,
            write_to_x,
            write_to_y,
            None,
            None,
            write_to_program_counter,
            write_to_isr,
            write_to_osr,
        ]

        self.out_destinations = [
            write_to_pins,
            write_to_x,
            write_to_y,
            write_to_null,
            write_to_pin_directions,
            None,
            None,
            None,
        ]

        self.set_destinations = [
            write_to_pins,
            write_to_x,
            write_to_y,
            None,
            write_to_pin_directions,
            None,
            None,
            None,
        ]

    def decode(self, opcode):
        """
        Decodes the given opcode and returns a callable which emulates it.

        Parameters:
        opcode (int): The opcode to decode.

        Returns:
        Instruction: Representation of the instruction or None.
        """

        decoding_function = self.decoding_functions[(opcode >> 13) & 7]
        return decoding_function(opcode)

    def _decode_jmp(self, opcode):
        address = opcode & 0x1F
        condition = self.jmp_conditions[(opcode >> 5) & 7]

        if condition is not None:
            return Instruction(
                condition,
                partial(write_to_program_counter, supplies_value(address)),
                ProgramCounterAdvance.WHEN_CONDITION_NOT_MET,
            )

        return None

    def _decode_mov(self, opcode):
        read_from_source = self.mov_sources[opcode & 7]

        destination = (opcode >> 5) & 7
        write_to_destination = self.mov_destinations[destination]

        if read_from_source is None or write_to_destination is None:
            return None

        operation = (opcode >> 3) & 3

        if operation == 1:
            data_supplier = lambda state: read_from_source(state) ^ 0xFFFF_FFFF
        else:
            data_supplier = read_from_source

        if destination == 5:  # Program counter
            program_counter_advance = ProgramCounterAdvance.NEVER
        else:
            program_counter_advance = ProgramCounterAdvance.ALWAYS

        return Instruction(
            always,
            partial(write_to_destination, data_supplier),
            program_counter_advance,
        )

    def _decode_in(self, opcode):
        read_from_source = self.in_sources[(opcode >> 5) & 7]

        bit_count = opcode & 0x1F

        if bit_count == 0:
            bit_count = 32

        return Instruction(
            always,
            partial(shift_into_isr, read_from_source, self.shift_isr_method, bit_count),
            ProgramCounterAdvance.ALWAYS,
        )

    def _decode_out(self, opcode):
        write_to_destination = self.out_destinations[(opcode >> 5) & 7]

        bit_count = opcode & 0x1F

        if bit_count == 0:
            bit_count = 32

        def emulate_out(state):
            state, shift_result = shift_from_osr(
                self.shift_osr_method, bit_count, state
            )
            return write_to_destination(supplies_value(shift_result), state)

        return Instruction(always, emulate_out, ProgramCounterAdvance.ALWAYS)

    def _decode_set(self, opcode):
        write_to_destination = self.set_destinations[(opcode >> 5) & 7]

        if write_to_destination is None:
            return None

        return Instruction(
            always,
            partial(write_to_destination, supplies_value(opcode & 0x1F)),
            ProgramCounterAdvance.ALWAYS,
        )

    @staticmethod
    def _decode_pull(opcode):
        if opcode & 0x0020:
            instruction = Instruction(
                transmit_fifo_not_empty,
                pull_blocking,
                ProgramCounterAdvance.WHEN_CONDITION_MET,
            )
        else:
            instruction = Instruction(
                always, pull_nonblocking, ProgramCounterAdvance.ALWAYS
            )

        return instruction

    @staticmethod
    def _decode_wait(opcode):
        index = opcode & 0x001F

        if opcode & 0x0080:
            condition = partial(gpio_high, index)
        else:
            condition = partial(gpio_low, index)

        return Instruction(
            condition, lambda state: state, ProgramCounterAdvance.WHEN_CONDITION_MET
        )
