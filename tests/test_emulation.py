# Copyright 2021, 2022, 2023, 2025 Nathan Young
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
import pytest

from pioemu import emulate
from pioemu.conditions import clock_cycles_reached
from tests.opcodes import Opcodes


def test_stop_when_requires_value():
    with pytest.raises(ValueError):
        next(emulate([0x0000], stop_when=None))


def test_emulation_stops_when_unsupported_opcode_is_reached():
    with pytest.raises(StopIteration):
        next(emulate([0xE0E0], stop_when=lambda opcode, _: False))


@pytest.mark.parametrize("threshold", [-1, 0, 33])
def test_validation_of_invalid_pull_threshold(threshold: int):
    with pytest.raises(ValueError):
        next(
            emulate(
                [Opcodes.nop()],
                stop_when=clock_cycles_reached(1),
                pull_threshold=threshold,
            )
        )


@pytest.mark.parametrize("threshold", [-1, 0, 33])
def test_validation_of_invalid_push_threshold(threshold: int):
    with pytest.raises(ValueError):
        next(
            emulate(
                [Opcodes.nop()],
                stop_when=clock_cycles_reached(1),
                push_threshold=threshold,
            )
        )
