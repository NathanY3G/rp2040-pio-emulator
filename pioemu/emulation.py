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
from functools import partial, wraps
from .state import State
from .conditions import (
    x_register_equals_zero,
    x_register_not_equal_to_y_register,
    x_register_not_equal_to_zero,
    y_register_equals_zero,
    y_register_not_equal_to_zero,
)
from .instructions import (
    jmp,
    jmp_when_x_is_non_zero_and_post_decrement,
    jmp_when_y_is_non_zero_and_post_decrement,
    mov_into_isr,
    mov_into_osr,
    mov_into_pins,
    mov_into_x,
    mov_into_y,
    out_null,
    out_pindirs,
    out_pins,
    out_x,
    out_y,
    pull_blocking,
    pull_nonblocking,
    set_pins,
    set_pindirs,
    set_x,
    set_y,
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
    opcodes, *, initial_state=State(), stop_condition=None, shift_osr_right=True
):
    stop_condition = stop_condition or (lambda state: False)

    if shift_osr_right:
        instruction_lookup = map_opcodes_to_callables(shift_right)
    else:
        instruction_lookup = map_opcodes_to_callables(shift_left)

    current_state = initial_state

    while not stop_condition(current_state):
        previous_state = current_state

        opcode = opcodes[current_state.program_counter]
        delay_value = (opcode >> 8) & 0x1F

        if (opcode >> 13) == 5:
            data_field = _read_source(MoveSource(opcode & 7), current_state)
        else:
            data_field = opcode & 0x1F

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


def _normalize_bit_count(function):
    @wraps(function)
    def wrapper(bit_count, state):
        if bit_count == 0:
            return function(32, state)
        else:
            return function(bit_count, state)

    return wrapper


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


def map_opcodes_to_callables(shifter_for_osr):
    return {
        0x0000: partial(jmp, lambda state: True),
        0x0020: partial(jmp, x_register_equals_zero),
        0x0040: jmp_when_x_is_non_zero_and_post_decrement,
        0x0060: partial(jmp, y_register_equals_zero),
        0x0080: jmp_when_y_is_non_zero_and_post_decrement,
        0x00A0: partial(jmp, x_register_not_equal_to_y_register),
        0x2020: wait_for_gpio_low,
        0x2080: wait_for_gpio_high,
        0x6000: _normalize_bit_count(partial(out_pins, shifter_for_osr)),
        0x6020: _normalize_bit_count(partial(out_x, shifter_for_osr)),
        0x6040: _normalize_bit_count(partial(out_y, shifter_for_osr)),
        0x6060: _normalize_bit_count(partial(out_null, shifter_for_osr)),
        0x6080: _normalize_bit_count(partial(out_pindirs, shifter_for_osr)),
        0x8080: pull_nonblocking,
        0x80A0: pull_blocking,
        0xA000: mov_into_pins,
        0xA020: mov_into_x,
        0xA040: mov_into_y,
        0xA0C0: mov_into_isr,
        0xA0E0: mov_into_osr,
        0xE080: set_pindirs,
        0xE000: set_pins,
        0xE020: set_x,
        0xE040: set_y,
    }
