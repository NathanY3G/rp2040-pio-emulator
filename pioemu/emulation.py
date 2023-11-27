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
from dataclasses import replace
from typing import Callable, Generator, List, Tuple

from .instruction import Instruction, ProgramCounterAdvance
from .instruction_decoder import InstructionDecoder
from .shift_register import ShiftRegister
from .state import State


def emulate(
    opcodes: List[int],
    *,
    stop_when: Callable[[int, State], bool],
    initial_state: State | None = None,
    input_source: Callable[[int], int] | None = None,
    shift_isr_right: bool = True,
    shift_osr_right: bool = True,
    side_set_base: int = 0,
    side_set_count: int = 0,
    jmp_pin: int = 0,
    wrap_target: int = 0,
    wrap_top: int = 0,
) -> Generator[Tuple[State, State], None, None]:
    """
    Create and return a generator for emulating the given PIO program.

    Parameters
    ----------
    opcodes : List[int]
        PIO program to emulate.
    stop_when : function
        Predicate used to determine if the emulation should stop or continue.
    initial_state : State, optional
        Initial values to use.
    shift_isr_right : bool, optional
        Shift the Input Shift Reigster (ISR) to the right when True and to the left when False.
    shift_osr_right : bool, optional
        Shift the Output Shift Reigster (OSR) to the right when True and to the left when False.
    side_set_base : int, optional
        First pin to use for the side-set.
    side_set_count : int
        Number of consecutive pins to include within the side-set.
    jmp_pin : int
        Pin that determines the branch taken by JMP PIN instructions.
    wrap_target : int
        Program counter value to wrap to when the program counter reaches the wrap_top value.
    wrap_top : int
        Program counter value to wrap from when the program counter reaches the wrap_top value.
        Defaults to len(opcodes) - 1.

    Returns
    -------
    generator
    """
    if stop_when is None:
        raise ValueError("emulate() missing value for keyword argument: 'stop_when'")

    shift_isr_method = (
        ShiftRegister.shift_right if shift_isr_right else ShiftRegister.shift_left
    )
    shift_osr_method = (
        ShiftRegister.shift_right if shift_osr_right else ShiftRegister.shift_left
    )

    instruction_decoder = InstructionDecoder(
        shift_isr_method, shift_osr_method, jmp_pin
    )

    wrap_top = wrap_top or len(opcodes) - 1

    current_state = initial_state if initial_state else State()
    stalled = False

    while not stop_when(opcodes[current_state.program_counter], current_state):
        previous_state = current_state

        if input_source:
            masked_values = current_state.pin_values & current_state.pin_directions
            masked_input = (
                input_source(current_state.clock) & ~current_state.pin_directions
            )
            current_state = replace(
                current_state,
                pin_values=masked_values | masked_input,
            )

        opcode = opcodes[current_state.program_counter]

        (side_set_value, delay_value) = _extract_delay_and_side_set_from_opcode(
            opcode, side_set_count
        )

        instruction = instruction_decoder.decode(opcode)

        if instruction is None:
            return

        condition_met = instruction.condition(current_state)
        if condition_met:
            new_state = instruction.callable(current_state)

            if new_state is not None:
                current_state = new_state
                stalled = False
            else:
                stalled = True

        current_state = _apply_side_effects(opcode, current_state)

        # TODO: Check that the following still applies when an instruction is stalled
        if side_set_count > 0:
            current_state = _apply_side_set_to_pin_values(
                current_state, side_set_base, side_set_count, side_set_value
            )

        if not stalled:
            current_state = _advance_program_counter(
                instruction, condition_met, wrap_target, wrap_top, current_state
            )

            current_state = _apply_delay_value(
                opcode, condition_met, delay_value, current_state
            )

        current_state = replace(current_state, clock=current_state.clock + 1)

        yield (previous_state, current_state)


def _advance_program_counter(
    instruction: Instruction,
    condition_met: bool,
    wrap_bottom: int,
    wrap_top: int,
    state: State,
) -> State:
    if state.program_counter == wrap_top:
        new_pc = wrap_bottom
    else:
        new_pc = state.program_counter + 1

    match instruction.program_counter_advance:
        case ProgramCounterAdvance.ALWAYS:
            return replace(state, program_counter=new_pc)
        case ProgramCounterAdvance.WHEN_CONDITION_MET if condition_met:
            return replace(state, program_counter=new_pc)
        case ProgramCounterAdvance.WHEN_CONDITION_NOT_MET if not condition_met:
            return replace(state, program_counter=new_pc)
        case _:
            return state


def _apply_delay_value(
    opcode: int, condition_met: bool, delay_value: int, state: State
) -> State:
    jump_instruction = (opcode >> 13) == 0

    if jump_instruction or condition_met:
        return replace(state, clock=state.clock + delay_value)

    return state


def _apply_side_effects(opcode: int, state: State) -> State:
    if (opcode & 0xE0E0) == 0x0040:
        return replace(state, x_register=state.x_register - 1)
    elif (opcode & 0xE0E0) == 0x0080:
        return replace(state, y_register=state.y_register - 1)
    else:
        return state


def _extract_delay_and_side_set_from_opcode(
    opcode: int, side_set_count: int
) -> Tuple[int, int]:
    combined_values = (opcode >> 8) & 0x1F
    bits_for_delay = 5 - side_set_count
    delay_mask = (1 << bits_for_delay) - 1

    return (combined_values >> bits_for_delay, combined_values & delay_mask)


def _apply_side_set_to_pin_values(
    state: State, pin_base: int, pin_count: int, pin_values: int
) -> State:
    bit_mask = ~(((1 << pin_count) - 1) << pin_base) & 0xFFFF
    new_pin_values = (state.pin_values & bit_mask) | (pin_values << pin_base)

    return replace(state, pin_values=new_pin_values)
