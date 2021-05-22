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
from dataclasses import replace
from enum import Enum, unique
from .instruction_decoder import InstructionDecoder
from .state import State
from .shifter import shift_left, shift_right


@unique
class MoveSource(Enum):
    PINS = 0
    X_REGISTER = 1
    Y_REGISTER = 2
    NULL = 3
    ISR = 6
    OSR = 7


def emulate(
    opcodes,
    *,
    initial_state=State(),
    stop_condition=None,
    shift_osr_right=True,
    side_set_base=0,
    side_set_count=0,
):
    stop_condition = stop_condition or (lambda state: False)

    if shift_osr_right:
        instruction_decoder = InstructionDecoder(shift_right)
    else:
        instruction_decoder = InstructionDecoder(shift_left)

    current_state = initial_state

    while not stop_condition(current_state):
        previous_state = current_state
        opcode = opcodes[current_state.program_counter]

        (side_set_value, delay_value) = _extract_delay_and_side_set_from_opcode(
            opcode, side_set_count
        )

        instruction = instruction_decoder.decode(opcode)

        # TODO: Consider moving this logic into the instruction decoder
        jump_instruction = (opcode >> 13) == 0
        move_instruction = (opcode >> 13) == 5

        if instruction is None:
            return

        if move_instruction:
            data_field = _read_source(MoveSource(opcode & 7), current_state)
        else:
            data_field = opcode & 0x1F

        condition_met = instruction.condition(current_state)
        if condition_met:
            current_state = instruction.callable(data_field, current_state)

        current_state = _apply_side_effects(opcode, current_state)

        # TODO: Check that the following still applies when an instruction is stalled
        if side_set_count > 0:
            current_state = _apply_side_set_to_pin_values(
                current_state, side_set_base, side_set_count, side_set_value
            )

        current_state = _advance_program_counter(
            condition_met, jump_instruction, current_state
        )

        current_state = _apply_delay_value(
            condition_met, jump_instruction, delay_value, current_state
        )

        yield (previous_state, current_state)


def _advance_program_counter(condition_met, jump_instruction, state):
    if condition_met and jump_instruction:
        return state
    elif not condition_met and not jump_instruction:
        return state
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


def _read_source(source, state):
    # TODO: Consider using the new match statement when widely available
    if source == MoveSource.PINS:
        value = state.pin_values
    elif source == MoveSource.X_REGISTER:
        value = state.x_register
    elif source == MoveSource.Y_REGISTER:
        value = state.y_register
    elif source == MoveSource.NULL:
        value = 0
    elif source == MoveSource.ISR:
        value = state.input_shift_register.contents
    elif source == MoveSource.OSR:
        value = state.output_shift_register.contents
    else:
        raise NotImplementedError("Source for move operation not supported yet")

    return value
