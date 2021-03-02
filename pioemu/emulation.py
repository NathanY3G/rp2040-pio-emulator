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


def emulate_opcodes(opcodes, initial_state):
    current_state = initial_state

    for opcode in opcodes:
        previous_state = current_state

        masked_opcode = opcode & 0xE0E0
        data_field = opcode & 0x1F

        if masked_opcode == 0x0:
            instruction = jmp_always
        elif masked_opcode == 0x2020:
            instruction = wait_for_gpio_low
        elif masked_opcode == 0x2080:
            instruction = wait_for_gpio_high
        elif masked_opcode == 0xE080:
            instruction = set_pindirs
        elif masked_opcode == 0xE000:
            instruction = set_pins
        elif masked_opcode == 0xE020:
            instruction = set_x
        elif masked_opcode == 0xE040:
            instruction = set_y
        else:
            instruction = None

        if instruction is not None:
            current_state = instruction(data_field, current_state)
            yield (previous_state, current_state)
        else:
            return (previous_state, None)


def next_instruction(state):
    return replace(state, program_counter=state.program_counter + 1)


def jmp_always(address, state):
    return replace(state, program_counter=address)


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

    if not state.pin_values & bit_mask:
        return next_instruction(state)
    else:
        return state


def wait_for_gpio_high(pin_number, state):
    bit_mask = 1 << pin_number

    if state.pin_values & bit_mask:
        return next_instruction(state)
    else:
        return state
