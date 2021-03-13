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
from pioemu import emulate, State


def test_jump_always_forward():
    _, new_state = next(emulate([0x0007], max_clock_cycles=1))  # jmp

    assert new_state.program_counter == 7


def test_jump_consumes_one_clock_cycle():
    _, new_state = next(emulate([0x0000], max_clock_cycles=1))  # jmp

    assert new_state.clock == 1
