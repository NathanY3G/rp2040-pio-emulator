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
from typing import Tuple

from pytest import param

from pioemu import clock_cycles_reached, emulate, State

from .opcodes import Opcodes


def instruction_param(
    description, opcode, initial_state, expected_state, *, expected_program_counter=None
):
    if expected_program_counter is not None:
        expected_state = replace(
            expected_state, clock=1, program_counter=expected_program_counter
        )
    else:
        expected_state = replace(expected_state, clock=1, program_counter=1)

    return param(opcode, initial_state, expected_state, id=description)


def emulate_single_instruction(
    opcode: int, *, initial_state=None, advance_program_counter=False
) -> Tuple[State, State]:
    if advance_program_counter:
        opcodes = [opcode, Opcodes.nop()]
    else:
        opcodes = [opcode]

    instruction_generator = emulate(
        opcodes,
        initial_state=initial_state if initial_state else None,
        stop_when=clock_cycles_reached(1),
    )

    return next(instruction_generator)
