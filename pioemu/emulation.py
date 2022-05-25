# Copyright 2021, 2022 Nathan Young
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
from .instruction_decoder import InstructionDecoder
from .shift_register import ShiftRegister
from .state import State


def emulate(
    opcodes,
    *,
    stop_when,
    initial_state=State(),
    input_source=None,
    shift_osr_right=True,
    side_set_base=0,
    side_set_count=0,
    jmp_pin=0,
):
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
    shift_osr_right : bool, optional
        Shift the Output Shift Reigster (OSR) to the right when True and to the left when False.
    side_set_base : int, optional
        First pin to use for the side-set.
    side_set_count : int
        Number of consecutive pins to include within the side-set.
    jmp_pin : int
        Pin that determines the branch taken by JMP PIN instructions.

    Returns
    -------
    generator
    """
    if stop_when is None:
        raise ValueError("emulate() missing value for keyword argument: 'stop_when'")

    if shift_osr_right:
        instruction_decoder = InstructionDecoder(ShiftRegister.shift_right, jmp_pin)
    else:
        instruction_decoder = InstructionDecoder(ShiftRegister.shift_left, jmp_pin)

    wrap_top = len(opcodes) - 1

    current_state = initial_state

    while not stop_when(opcodes[current_state.program_counter], current_state):
        previous_state = current_state

        if input_source:
            current_state = replace(
                current_state,
                pin_values=input_source(current_state.clock)
                & ~current_state.pin_directions,
            )

        opcode = opcodes[current_state.program_counter]

        (side_set_value, delay_value) = _extract_delay_and_side_set_from_opcode(
            opcode, side_set_count
        )

        instruction = instruction_decoder.decode(opcode)

        # TODO: Consider moving this logic into the instruction decoder
        jump_instruction = (opcode >> 13) == 0

        if instruction is None:
            return

        condition_met = instruction.condition(current_state)
        if condition_met:
            current_state = instruction.callable(current_state)

        current_state = _apply_side_effects(opcode, current_state)

        # TODO: Check that the following still applies when an instruction is stalled
        if side_set_count > 0:
            current_state = _apply_side_set_to_pin_values(
                current_state, side_set_base, side_set_count, side_set_value
            )

        current_state = _advance_program_counter(
            condition_met, jump_instruction, 0, wrap_top, current_state
        )

        current_state = _apply_delay_value(
            condition_met, jump_instruction, delay_value, current_state
        )

        yield (previous_state, current_state)


def _advance_program_counter(
    condition_met, jump_instruction, wrap_bottom, wrap_top, state
):
    if condition_met and jump_instruction:
        return state
    elif not condition_met and not jump_instruction:
        return state
    elif state.program_counter == wrap_top:
        return replace(state, program_counter=wrap_bottom)
    else:
        return replace(state, program_counter=state.program_counter + 1)


def _apply_delay_value(condition_met, jump_instruction, delay_value, state):
    if jump_instruction or condition_met:
        return replace(state, clock=state.clock + 1 + delay_value)
    else:
        return replace(state, clock=state.clock + 1)


def _apply_side_effects(opcode, state):
    if (opcode & 0xE0E0) == 0x0040:
        return replace(state, x_register=state.x_register - 1)
    elif (opcode & 0xE0E0) == 0x0080:
        return replace(state, y_register=state.y_register - 1)
    else:
        return state


def _extract_delay_and_side_set_from_opcode(opcode, side_set_count):
    combined_values = (opcode >> 8) & 0x1F
    bits_for_delay = 5 - side_set_count
    delay_mask = (1 << bits_for_delay) - 1

    return (combined_values >> bits_for_delay, combined_values & delay_mask)


def _apply_side_set_to_pin_values(state, pin_base, pin_count, pin_values):
    bit_mask = ~(((1 << pin_count) - 1) << pin_base) & 0xFFFF
    new_pin_values = (state.pin_values & bit_mask) | (pin_values << pin_base)

    return replace(state, pin_values=new_pin_values)
