# Copyright 2021, 2023 Nathan Young
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
from ..conditions import transmit_fifo_empty
from ..shift_register import ShiftRegister
from ..state import State


def pull_blocking(state: State) -> State | None:
    if transmit_fifo_empty(state):
        return None  # Represents a stall

    updated_transmit_fifo = state.transmit_fifo.copy()

    return replace(
        state,
        transmit_fifo=updated_transmit_fifo,
        output_shift_register=ShiftRegister(updated_transmit_fifo.popleft(), 0),
    )


def pull_nonblocking(state: State) -> State:
    updated_transmit_fifo = state.transmit_fifo.copy()

    if transmit_fifo_empty(state):
        new_contents = state.x_register
    else:
        new_contents = updated_transmit_fifo.popleft()

    return replace(
        state,
        transmit_fifo=updated_transmit_fifo,
        output_shift_register=ShiftRegister(new_contents, 0),
    )
