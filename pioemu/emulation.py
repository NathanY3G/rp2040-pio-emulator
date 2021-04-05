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
from functools import partial
from .state import State
from .conditions import (
    x_register_equals_zero,
    x_register_not_equal_to_y_register,
    x_register_not_equal_to_zero,
    y_register_equals_zero,
    y_register_not_equal_to_zero,
)


def emulate(opcodes, *, initial_state=State(), stop_condition=None):
    stop_condition = stop_condition or (lambda state: False)

    instruction_lookup = map_opcodes_to_callables()

    current_state = initial_state

    while not stop_condition(current_state):
        previous_state = current_state

        opcode = opcodes[current_state.program_counter]
        data_field = opcode & 0x1F
        delay_value = (opcode >> 8) & 0x1F

        instruction = instruction_lookup.get(opcode & 0xE0E0, None)
        if instruction is None:
            return

        current_state = instruction(data_field, current_state)

        if is_instruction_stalled(previous_state, current_state, instruction):
            clock_cycles_consumed = 1
        else:
            clock_cycles_consumed = 1 + delay_value

        current_state = replace(
            current_state, clock=current_state.clock + clock_cycles_consumed
        )

        yield (previous_state, current_state)


def is_instruction_stalled(previous_state, current_state, instruction):
    if instruction in [pull_blocking, wait_for_gpio_low, wait_for_gpio_high]:
        return current_state.program_counter == previous_state.program_counter
    else:
        return False


def next_instruction(state):
    return replace(state, program_counter=state.program_counter + 1)


def jump(condition, address, state):
    if condition(state):
        return replace(state, program_counter=address)
    else:
        return next_instruction(state)


def jump_when_x_is_non_zero_and_post_decrement(address, state):
    return replace(
        jump(x_register_not_equal_to_zero, address, state),
        x_register=state.x_register - 1,
    )


def jump_when_y_is_non_zero_and_post_decrement(address, state):
    return replace(
        jump(y_register_not_equal_to_zero, address, state),
        y_register=state.y_register - 1,
    )


def pull_blocking(not_used, state):
    if len(state.transmit_fifo) > 0:
        return next_instruction(replace(state, output_shift_register=state.transmit_fifo.pop()))
    else:
        return state


def pull_nonblocking(not_used, state):
    if len(state.transmit_fifo) > 0:
        return next_instruction(replace(state, output_shift_register=state.transmit_fifo.pop()))
    else:
        return next_instruction(replace(state, output_shift_register=state.x_register))


def set_pins(data, state):
    return next_instruction(replace(state, pin_values=data))


def set_pindirs(data, state):
    return next_instruction(replace(state, pin_directions=data))


def set_x(data, state):
    return next_instruction(replace(state, x_register=data))


def set_y(data, state):
    return next_instruction(replace(state, y_register=data))


def wait_for_gpio_low(pin_number, state):
    bit_mask = 1 << pin_number
    return next_instruction(state) if not state.pin_values & bit_mask else state


def wait_for_gpio_high(pin_number, state):
    bit_mask = 1 << pin_number
    return next_instruction(state) if state.pin_values & bit_mask else state


def map_opcodes_to_callables():
    return {
        0x0000: partial(jump, lambda state: True),
        0x0020: partial(jump, x_register_equals_zero),
        0x0040: jump_when_x_is_non_zero_and_post_decrement,
        0x0060: partial(jump, y_register_equals_zero),
        0x0080: jump_when_y_is_non_zero_and_post_decrement,
        0x00A0: partial(jump, x_register_not_equal_to_y_register),
        0x2020: wait_for_gpio_low,
        0x2080: wait_for_gpio_high,
        0x8080: pull_nonblocking,
        0x80A0: pull_blocking,
        0xE080: set_pindirs,
        0xE000: set_pins,
        0xE020: set_x,
        0xE040: set_y,
    }
