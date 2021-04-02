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
from pioemu import clock_cycles_reached, emulate, State


def emulate_single_instruction(opcode, initial_state=None):
    if initial_state is not None:
        instruction_generator = emulate(
            [opcode],
            initial_state=initial_state,
            stop_condition=clock_cycles_reached(1),
        )
    else:
        instruction_generator = emulate(
            [opcode], stop_condition=clock_cycles_reached(1)
        )

    _, new_state = next(instruction_generator)

    return new_state
