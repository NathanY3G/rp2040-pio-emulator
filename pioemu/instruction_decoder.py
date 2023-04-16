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
from typing import Callable, List, Tuple

from .conditions import (
    always,
    gpio_low,
    gpio_high,
    input_shift_register_full,
    negate,
    output_shift_register_empty,
    x_register_equals_zero,
    x_register_not_equal_to_y_register,
    x_register_not_equal_to_zero,
    y_register_equals_zero,
    y_register_not_equal_to_zero,
)
from .instruction import Instruction, ProgramCounterAdvance
from .instructions.pull import (
    pull_blocking,
    pull_nonblocking,
)
from .instructions.push import (
    push_blocking,
    push_nonblocking,
)
from .primitive_operations import (
    read_from_isr,
    shift_into_isr,
    read_from_osr,
    shift_from_osr,
    read_from_pins,
    read_from_x,
    read_from_y,
    stall_unless_predicate_met,
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
from .shift_register import ShiftRegister
from .state import State


class InstructionDecoder:
    """
    Decodes opcodes representing instructions into callables that emulate those
    instructions.
    """

    def __init__(
        self,
        shift_isr_method: Callable[[ShiftRegister, int], Tuple[ShiftRegister, int]],
        shift_osr_method: Callable[[ShiftRegister, int], Tuple[ShiftRegister, int]],
        jmp_pin: int,
    ):
        """
        Parameters
        ----------
        isr_shift_method : Callable[[ShiftRegister, int], Tuple[ShiftRegister, int]]
            Method to use to shift the contents of the Input Shift Register.
        osr_shift_method : Callable[[ShiftRegister, int], Tuple[ShiftRegister, int]]
            Method to use to shift the contents of the Output Shift Register.
        jmp_pin : int
            Pin that determines the branch taken by JMP PIN instructions.
        """

        self.shift_isr_method = shift_isr_method
        self.shift_osr_method = shift_osr_method

        self.decoding_functions: List[Callable[[int], Instruction | None]] = [
            self._decode_jmp,
            self._decode_wait,
            self._decode_in,
            self._decode_out,
            self._decode_push_pull,
            self._decode_mov,
            lambda _: None,
            self._decode_set,
        ]

        self.jmp_conditions: List[Callable[[State], bool]] = [
            always,
            x_register_equals_zero,
            x_register_not_equal_to_zero,
            y_register_equals_zero,
            y_register_not_equal_to_zero,
            x_register_not_equal_to_y_register,
            partial(gpio_high, jmp_pin),
            negate(output_shift_register_empty),
        ]

        self.in_sources: List[Callable[[State], int] | None] = [
            read_from_pins,
            read_from_x,
            read_from_y,
            supplies_value(0),
            None,
            None,
            read_from_isr,
            read_from_osr,
        ]

        self.mov_sources: List[Callable[[State], int] | None] = [
            read_from_pins,
            read_from_x,
            read_from_y,
            supplies_value(0),
            None,
            None,
            read_from_isr,
            read_from_osr,
        ]

        self.mov_destinations: List[
            Callable[[Callable[[State], int], State], State] | None
        ] = [
            write_to_pins,
            write_to_x,
            write_to_y,
            None,
            None,
            write_to_program_counter,
            write_to_isr,
            write_to_osr,
        ]

        # FIXME: Different signature used by write_to_isr() conflicts with type-hints
        self.out_destinations = [
            write_to_pins,
            write_to_x,
            write_to_y,
            write_to_null,
            write_to_pin_directions,
            write_to_program_counter,
            write_to_isr,
            None,
        ]

        self.set_destinations: List[
            Callable[[Callable[[State], int], State], State] | None
        ] = [
            write_to_pins,
            write_to_x,
            write_to_y,
            None,
            write_to_pin_directions,
            None,
            None,
            None,
        ]

    def decode(self, opcode: int) -> Instruction | None:
        """
        Decodes the given opcode and returns a callable which emulates it.

        Parameters:
        opcode (int): The opcode to decode.

        Returns:
        Instruction: Representation of the instruction or None.
        """

        decoding_function = self.decoding_functions[(opcode >> 13) & 7]
        return decoding_function(opcode)

    def _decode_jmp(self, opcode: int) -> Instruction | None:
        address = opcode & 0x1F
        condition = self.jmp_conditions[(opcode >> 5) & 7]

        if condition is not None:
            return Instruction(
                condition,
                partial(write_to_program_counter, supplies_value(address)),
                ProgramCounterAdvance.WHEN_CONDITION_NOT_MET,
            )

        return None

    def _decode_mov(self, opcode: int) -> Instruction | None:
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

    def _decode_in(self, opcode: int) -> Instruction | None:
        read_from_source = self.in_sources[(opcode >> 5) & 7]

        bit_count = opcode & 0x1F

        if bit_count == 0:
            bit_count = 32

        return Instruction(
            always,
            partial(shift_into_isr, read_from_source, self.shift_isr_method, bit_count),
            ProgramCounterAdvance.ALWAYS,
        )

    def _decode_out(self, opcode: int) -> Instruction | None:
        destination = (opcode >> 5) & 7
        write_to_destination = self.out_destinations[destination]

        bit_count = opcode & 0x1F

        if bit_count == 0:
            bit_count = 32

        if write_to_destination is None:
            return None

        def emulate_out(state: State) -> State:
            state, shift_result = shift_from_osr(
                self.shift_osr_method, bit_count, state
            )

            # Somewhat hacky workaround because 'OUT, ISR' also sets ISR shift counter to the
            # bit_count but no other command where the ISR is written to has a similar effect.
            # See the description of the ISR destination on section 3.4.5.2 of the RP2040 Datasheet
            if write_to_destination == write_to_isr:
                return write_to_destination(
                    supplies_value(shift_result), state, count=bit_count
                )

            return write_to_destination(supplies_value(shift_result), state)

        if destination == 5:  # Program counter
            return Instruction(always, emulate_out, ProgramCounterAdvance.NEVER)

        return Instruction(always, emulate_out, ProgramCounterAdvance.ALWAYS)

    def _decode_set(self, opcode: int) -> Instruction | None:
        write_to_destination = self.set_destinations[(opcode >> 5) & 7]

        if write_to_destination is None:
            return None

        return Instruction(
            always,
            partial(write_to_destination, supplies_value(opcode & 0x1F)),
            ProgramCounterAdvance.ALWAYS,
        )

    @staticmethod
    def _decode_push_pull(opcode: int) -> Instruction:
        block = bool(opcode & 0x0020)

        if opcode & 0x0080:
            # Pull
            condition = output_shift_register_empty if (opcode & 0x0040) else always

            instruction = Instruction(
                condition,
                pull_blocking if block else pull_nonblocking,
                ProgramCounterAdvance.ALWAYS,
            )
        else:
            # Push
            condition = input_shift_register_full if (opcode & 0x0040) else always

            instruction = Instruction(
                condition,
                push_blocking if block else push_nonblocking,
                ProgramCounterAdvance.ALWAYS,
            )

        return instruction

    @staticmethod
    def _decode_wait(opcode: int) -> Instruction | None:
        index = opcode & 0x001F

        if opcode & 0x0080:
            condition = partial(gpio_high, index)
        else:
            condition = partial(gpio_low, index)

        return Instruction(
            always,
            partial(stall_unless_predicate_met, condition),
            ProgramCounterAdvance.ALWAYS,
        )
