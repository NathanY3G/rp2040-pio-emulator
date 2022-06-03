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
import pytest
import subprocess
from pioemu import clock_cycles_reached, emulate, State

PIO_SOURCE_FILENAME = "blinkt_example.pio"
NUMBER_OF_LEDS = 8


@pytest.fixture
def assembled_program():
    output = subprocess.run(
        ["pioasm", "-o", "hex", PIO_SOURCE_FILENAME], capture_output=True
    )
    if output.returncode != 0:
        raise ValueError(f"Unable to assemble PIO program {PIO_SOURCE_FILENAME}")

    return [int(opcode, 16) for opcode in output.stdout.decode("utf-8").split()]


def test_example_generates_blue_pixel_sequence(assembled_program):
    def _stop_after_one_iteration(_, state):
        return state.program_counter >= len(assembled_program) - 1

    # Create a generator which will emulate a single instruction at a time.
    # Each invocation yields a tuple containing two values; the state before
    # the instruction was executed and the state after.
    state_change_generator = emulate(
        assembled_program, stop_when=_stop_after_one_iteration
    )

    # Use a list comprehension to extract just the values on the Clock and Data
    # pins as they change over time.
    clock_and_data_sequence = [
        _extract_clock_and_data(after.pin_values)
        for before, after in state_change_generator
        if before.pin_values != after.pin_values
    ]

    assert clock_and_data_sequence == expected_sequence(
        red_on=False, green_on=False, blue_on=True
    )


def expected_sequence(red_on, green_on, blue_on):
    """Generates clock and data sequence expected by the Pimoroni Blinkt! for the colour specified"""

    zero = [(1, 0), (0, 0)]  # Clock and data sequence representing a zero (0)
    one = [(1, 1), (0, 1)]  # Clock and data sequence representing a zero (1)

    brightness = one * 8
    red = (one if red_on else zero) * 8
    green = (one if green_on else zero) * 8
    blue = (one if blue_on else zero) * 8

    start_sequence = end_sequence = zero * 32

    return (
        start_sequence
        + (brightness + blue + green + red) * NUMBER_OF_LEDS
        + end_sequence
    )


def _extract_clock_and_data(pin_values):
    return ((pin_values >> 1) & 1, pin_values & 1)
