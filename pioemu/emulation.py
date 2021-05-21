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
from .instructions import (
    pull_blocking,
    wait_for_gpio_low,
    wait_for_gpio_high,
)
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
    side_set_count=0
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

        if (opcode >> 13) == 5:
            data_field = _read_source(MoveSource(opcode & 7), current_state)
        else:
            data_field = opcode & 0x1F

        instruction = instruction_decoder.decode(opcode)

        if instruction is None:
            return

        current_state = instruction(data_field, current_state)

        if is_instruction_stalled(previous_state, current_state, instruction):
            clock_cycles_consumed = 1
        else:
            clock_cycles_consumed = 1 + delay_value

        if side_set_count > 0:
            current_state = _apply_side_set_to_pin_values(
                current_state, side_set_base, side_set_count, side_set_value
            )

        current_state = replace(
            current_state, clock=current_state.clock + clock_cycles_consumed
        )

        yield (previous_state, current_state)


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


def is_instruction_stalled(previous_state, current_state, instruction):
    if instruction in [pull_blocking, wait_for_gpio_low, wait_for_gpio_high]:
        return current_state.program_counter == previous_state.program_counter
    else:
        return False
