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
from pioemu import State, emulate


def test_programs_wrap_by_default():
    x_register_series = [
        state.x_register
        for _, state in emulate(
            [0xA029],  # invert all bits in the X register on each invocation
            stop_when=lambda _, state: state.clock == 3,
            initial_state=State(x_register=0),
        )
    ]

    assert x_register_series == [0xFFFF_FFFF, 0x0000_0000, 0xFFFF_FFFF]
