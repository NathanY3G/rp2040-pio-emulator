# Copyright 2021, 2022, 2023, 2025 Nathan Young
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
from typing import Callable, List, Optional, Tuple

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
from .instruction import (
    Emulation,
    InInstruction,
    Instruction,
    JmpInstruction,
    OutInstruction,
    ProgramCounterAdvance,
    PullInstruction,
    PushInstruction,
    WaitInstruction,
)
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

        self.decoding_functions: List[Callable[[int], Optional[Emulation]]] = [
            lambda _: None,
            lambda _: None,
            lambda _: None,
            lambda _: None,
            lambda _: None,
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

    def create_emulation(
        self, instruction: Optional[Instruction]
    ) -> Optional[Emulation]:
        """
        Returns an emulation for the given instruction.

        Parameters:
        instruction (Instruction): The instruction to be emulated.

        Returns:
        Emulation: Emulation for the given instruction or None when invalid/not supported
        """

        match instruction:
            case InInstruction():
                emulation = self._decode_in(instruction)
            case JmpInstruction():
                emulation = self._decode_jmp(instruction)
            case OutInstruction():
                emulation = self._decode_out(instruction)
            case PullInstruction():
                emulation = self._decode_pull(instruction)
            case PushInstruction():
                emulation = self._decode_push(instruction)
            case WaitInstruction():
                emulation = self._decode_wait(instruction)
            case _:
                emulation = None

        return emulation

    def decode(self, opcode: int) -> Optional[Emulation]:
        """
        Decodes the given opcode and returns a callable which emulates it.

        Parameters:
        opcode (int): The opcode to decode.

        Returns:
        Emulation: Emulation for the given opcode or None when invalid/not supported
        """

        decoding_function = self.decoding_functions[(opcode >> 13) & 7]
        return decoding_function(opcode)

    def _decode_jmp(self, instruction: JmpInstruction) -> Optional[Emulation]:
        condition = self.jmp_conditions[instruction.condition]

        if condition is None:
            return None

        return Emulation(
            condition,
            partial(
                write_to_program_counter, supplies_value(instruction.target_address)
            ),
            ProgramCounterAdvance.WHEN_CONDITION_NOT_MET,
            instruction,
        )

    def _decode_mov(self, opcode: int) -> Optional[Emulation]:
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

        return Emulation(
            always,
            partial(write_to_destination, data_supplier),
            program_counter_advance,
        )

    def _decode_in(self, instruction: InInstruction) -> Emulation:
        read_from_source = self.in_sources[instruction.source]

        return Emulation(
            always,
            partial(
                shift_into_isr,
                read_from_source,
                self.shift_isr_method,
                instruction.bit_count,
            ),
            ProgramCounterAdvance.ALWAYS,
            instruction,
        )

    def _decode_out(self, instruction: OutInstruction) -> Optional[Emulation]:
        write_to_destination = self.out_destinations[instruction.destination]

        if write_to_destination is None:
            return None

        def emulate_out(state: State) -> State:
            state, shift_result = shift_from_osr(
                self.shift_osr_method, instruction.bit_count, state
            )

            # Somewhat hacky workaround because 'OUT, ISR' also sets ISR shift counter to the
            # bit_count but no other command where the ISR is written to has a similar effect.
            # See the description of the ISR destination on section 3.4.5.2 of the RP2040 Datasheet
            if write_to_destination == write_to_isr:
                return write_to_destination(
                    supplies_value(shift_result), state, count=instruction.bit_count
                )

            return write_to_destination(supplies_value(shift_result), state)

        if instruction.destination == 5:  # Program counter
            program_counter_advance = ProgramCounterAdvance.NEVER
        else:
            program_counter_advance = ProgramCounterAdvance.ALWAYS

        return Emulation(
            always,
            emulate_out,
            program_counter_advance,
            instruction,
        )

    def _decode_set(self, opcode: int) -> Optional[Emulation]:
        write_to_destination = self.set_destinations[(opcode >> 5) & 7]

        if write_to_destination is None:
            return None

        return Emulation(
            always,
            partial(write_to_destination, supplies_value(opcode & 0x1F)),
            ProgramCounterAdvance.ALWAYS,
        )

    @staticmethod
    def _decode_pull(instruction: PullInstruction) -> Emulation:
        condition = output_shift_register_empty if instruction.if_empty else always

        return Emulation(
            condition,
            pull_blocking if instruction.block else pull_nonblocking,
            ProgramCounterAdvance.ALWAYS,
            instruction,
        )

    @staticmethod
    def _decode_push(instruction: PushInstruction) -> Emulation:
        condition = input_shift_register_full if instruction.if_full else always

        return Emulation(
            condition,
            push_blocking if instruction.block else push_nonblocking,
            ProgramCounterAdvance.ALWAYS,
            instruction,
        )

    @staticmethod
    def _decode_wait(instruction: WaitInstruction) -> Emulation:
        if instruction.polarity:
            condition = partial(gpio_high, instruction.index)
        else:
            condition = partial(gpio_low, instruction.index)

        return Emulation(
            always,
            partial(stall_unless_predicate_met, condition),
            ProgramCounterAdvance.ALWAYS,
        )
