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
from pioemu import emulate
from functools import reduce
from ..opcodes import Opcodes


def _execute_test_program(stop_condition):
    # Program which decrements the X register from 9 down to 0
    opcodes = [0xE029, 0xA041, 0x0041, Opcodes.nop()]

    return reduce(
        lambda _, states_tuple: states_tuple[1],
        emulate(opcodes, stop_when=stop_condition),
    )


def test_execution_stops_after_fifth_clock_cycle():
    state_when_stopped = _execute_test_program(lambda _, state: state.clock == 5)
    assert state_when_stopped.clock == 5


def test_execution_stops_when_nop_reached():
    state_when_stopped = _execute_test_program(lambda opcode, _: opcode == Opcodes.nop())
    assert state_when_stopped.program_counter == 3


def test_execution_stops_when_x_equals_one():
    state_when_stopped = _execute_test_program(lambda _, state: state.x_register == 1)
    assert state_when_stopped.x_register == 1
