# Copyright 2021, 2022, 2023, 2024, 2025 Nathan Young
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
import inspect
import logging
from dataclasses import replace
from typing import Callable, Generator, List, Optional, Tuple

from .decoding.instruction_decoder import InstructionDecoder as NewInstructionDecoder
from .instruction import (
    Emulation,
    InInstruction,
    Instruction,
    JmpInstruction,
    OutInstruction,
    ProgramCounterAdvance,
)
from .instruction_decoder import InstructionDecoder
from .shift_register import ShiftRegister
from .state import State


def emulate(
    opcodes: List[int],
    *,
    stop_when: Callable[[int, State], bool],
    initial_state: State | None = None,
    input_source: Callable[[State], int] | Callable[[int], int] | None = None,
    auto_pull: bool = False,
    auto_push: bool = False,
    pull_threshold: int = 32,
    push_threshold: int = 32,
    shift_isr_right: bool = True,
    shift_osr_right: bool = True,
    side_set_base: int = 0,
    side_set_count: int = 0,
    jmp_pin: int = 0,
    wrap_target: int = 0,
    wrap_top: int = 0,
) -> Generator[Tuple[State, State], None, None]:
    """
    Create and return a generator for emulating the given PIO program.

    Parameters
    ----------
    opcodes : List[int]
        PIO program to emulate.
    stop_when : function
        Predicate used to determine if the emulation should stop or continue.
    initial_state : State, optional
        Initial values to use.
    input_source : Callable, optional
        Invoked before each instruction to obtain the values currently present on the GPIO pins.
    auto_pull : bool, optional
        Automatically refill the Output Shift Reigster (OSR) from its associated FIFO when True.
    auto_push : bool, optional
        Automatically transfer the Input Shift Register (ISR) into its associated FIFO when True.
    pull_threshold : int, optional
        Number of bits shifted into Input Shift Register (ISR) before auto-push will take place.
    push_threshold : int, optional
        Number of bits shifted out of Output Shift Register (OSR) before auto-pull will take place.
    shift_isr_right : bool, optional
        Shift the Input Shift Reigster (ISR) to the right when True and to the left when False.
    shift_osr_right : bool, optional
        Shift the Output Shift Reigster (OSR) to the right when True and to the left when False.
    side_set_base : int, optional
        First pin to use for the side-set.
    side_set_count : int
        Number of consecutive pins to include within the side-set.
    jmp_pin : int
        Pin that determines the branch taken by JMP PIN instructions.
    wrap_target : int
        Program counter value to wrap to when the program counter reaches the wrap_top value.
    wrap_top : int
        Program counter value to wrap from when the program counter reaches the wrap_top value.
        Defaults to len(opcodes) - 1.

    Returns
    -------
    generator
    """
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.WARNING)
    logger = logging.getLogger(__name__)

    if pull_threshold < 1 or pull_threshold > 32:
        raise ValueError(
            "emulate() invalid value for keyword argument: 'pull_threshold'"
        )

    if push_threshold < 1 or push_threshold > 32:
        raise ValueError(
            "emulate() invalid value for keyword argument: 'push_threshold'"
        )

    if stop_when is None:
        raise ValueError("emulate() missing value for keyword argument: 'stop_when'")

    if input_source:
        input_source = _normalize_input_source(logger, input_source)

    shift_isr_method = (
        ShiftRegister.shift_right if shift_isr_right else ShiftRegister.shift_left
    )
    shift_osr_method = (
        ShiftRegister.shift_right if shift_osr_right else ShiftRegister.shift_left
    )

    new_instruction_decoder = NewInstructionDecoder(side_set_count)

    old_instruction_decoder = InstructionDecoder(
        shift_isr_method, shift_osr_method, jmp_pin
    )

    wrap_top = wrap_top or len(opcodes) - 1

    current_state = initial_state if initial_state else State()
    stalled = False

    while not stop_when(opcodes[current_state.program_counter], current_state):
        previous_state = current_state

        if input_source:
            masked_values = current_state.pin_values & current_state.pin_directions
            masked_input = input_source(current_state) & ~current_state.pin_directions
            current_state = replace(
                current_state,
                pin_values=masked_values | masked_input,
            )

        opcode = opcodes[current_state.program_counter]

        (side_set_value, delay_value) = _extract_delay_and_side_set_from_opcode(
            opcode, side_set_count
        )

        instruction = new_instruction_decoder.decode(opcode)

        emulation = (
            old_instruction_decoder.create_emulation(instruction)
            if instruction
            else old_instruction_decoder.decode(opcode)
        )

        if emulation is None:
            return

        condition_met = emulation.condition(current_state)
        if condition_met:
            # Stall the state machine if it attempts to automatically push the contents of the ISR
            # into a full FIFO. Please refer to the Autopush Details section (3.5.4.1) within the
            # RP2040 Datasheet for more details.
            if (
                isinstance(instruction, InInstruction)
                and auto_push
                and current_state.input_shift_register.counter >= push_threshold
                and len(current_state.receive_fifo) >= 4
            ):
                new_state = None

            # Stall the state machine if it attempts to fill an empty OSR and execute 'OUT' within
            # the same clock cycle. Please refer to the Autopull Details section (3.4.5.2) within
            # the RP2040 Datasheet for more details.
            elif (
                isinstance(instruction, OutInstruction)
                and auto_pull
                and current_state.output_shift_register.counter >= pull_threshold
            ):
                new_state = None
            else:
                new_state = emulation.emulate(current_state)

            if new_state is not None:
                current_state = new_state
                stalled = False
            else:
                stalled = True

        current_state = _apply_side_effects(
            instruction,
            opcode,
            current_state,
            auto_push,
            push_threshold,
            auto_pull,
            pull_threshold,
        )

        # TODO: Check that the following still applies when an instruction is stalled
        if side_set_count > 0:
            current_state = _apply_side_set_to_pin_values(
                current_state, side_set_base, side_set_count, side_set_value
            )

        if not stalled:
            current_state = _advance_program_counter(
                emulation, condition_met, wrap_target, wrap_top, current_state
            )

            current_state = _apply_delay_value(
                instruction, condition_met, delay_value, current_state
            )

        current_state = replace(current_state, clock=current_state.clock + 1)

        yield (previous_state, current_state)


def _normalize_input_source(logger: logging.Logger, input_source: Callable):
    parameter_type = _get_input_source_parameter_type(input_source)

    if parameter_type == State:
        return input_source
    elif parameter_type == int:
        return lambda state: input_source(state.clock)
    elif parameter_type is None:
        logger.warning(
            "input_source is missing type hints/annotations and may not work as expected"
        )
        return lambda state: input_source(state.clock)
    else:
        raise ValueError("Unsupported signature for input_source")


def _get_input_source_parameter_type(input_source: Callable):
    parameters = list(inspect.signature(input_source).parameters.values())

    if len(parameters) != 1:
        raise ValueError("Unsupported signature for input_source")

    parameter_type = parameters[0].annotation

    return parameter_type if parameter_type != inspect._empty else None


def _advance_program_counter(
    emulation: Emulation,
    condition_met: bool,
    wrap_bottom: int,
    wrap_top: int,
    state: State,
) -> State:
    if state.program_counter == wrap_top:
        new_pc = wrap_bottom
    else:
        new_pc = state.program_counter + 1

    match emulation.program_counter_advance:
        case ProgramCounterAdvance.ALWAYS:
            return replace(state, program_counter=new_pc)
        case ProgramCounterAdvance.WHEN_CONDITION_MET if condition_met:
            return replace(state, program_counter=new_pc)
        case ProgramCounterAdvance.WHEN_CONDITION_NOT_MET if not condition_met:
            return replace(state, program_counter=new_pc)
        case _:
            return state


def _apply_delay_value(
    instruction: Optional[Instruction],
    condition_met: bool,
    delay_value: int,
    state: State,
) -> State:
    if isinstance(instruction, JmpInstruction) or condition_met:
        return replace(state, clock=state.clock + delay_value)

    return state


def _apply_side_effects(
    instruction: Optional[Instruction],
    opcode: int,
    state: State,
    auto_push: bool,
    push_threshold: int,
    auto_pull: bool,
    pull_threshold: int,
) -> State:
    if (
        isinstance(instruction, InInstruction)
        and auto_push
        and state.input_shift_register.counter >= push_threshold
        and len(state.receive_fifo) < 4
    ):
        new_receive_fifo = state.receive_fifo.copy()
        new_receive_fifo.append(state.input_shift_register.contents)
        new_input_shift_register = ShiftRegister(0, 0)

        return replace(
            state,
            receive_fifo=new_receive_fifo,
            input_shift_register=new_input_shift_register,
        )
    elif (
        isinstance(instruction, OutInstruction)
        and auto_pull
        and state.output_shift_register.counter >= pull_threshold
        and state.transmit_fifo
    ):
        new_transmit_fifo = state.transmit_fifo.copy()
        new_output_shift_register = ShiftRegister(new_transmit_fifo.popleft(), 0)

        return replace(
            state,
            transmit_fifo=new_transmit_fifo,
            output_shift_register=new_output_shift_register,
        )
    elif (opcode & 0xE0E0) == 0x0040:
        return replace(state, x_register=state.x_register - 1)
    elif (opcode & 0xE0E0) == 0x0080:
        return replace(state, y_register=state.y_register - 1)

    return state


def _extract_delay_and_side_set_from_opcode(
    opcode: int, side_set_count: int
) -> Tuple[int, int]:
    combined_values = (opcode >> 8) & 0x1F
    bits_for_delay = 5 - side_set_count
    delay_mask = (1 << bits_for_delay) - 1

    return (combined_values >> bits_for_delay, combined_values & delay_mask)


def _apply_side_set_to_pin_values(
    state: State, pin_base: int, pin_count: int, pin_values: int
) -> State:
    bit_mask = ~(((1 << pin_count) - 1) << pin_base) & 0xFFFF_FFFF
    new_pin_values = (state.pin_values & bit_mask) | (pin_values << pin_base)

    return replace(state, pin_values=new_pin_values)
