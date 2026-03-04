"""Disassembler for RP2040 PIO opcodes."""
# Copyright 2026 Ned Konz <ned@metamagix.tech>
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
from pioemu.decoding.instruction_decoder import InstructionDecoder
from pioemu.instruction import (
    InInstruction,
    IrqInstruction,
    JmpInstruction,
    OutInstruction,
    PullInstruction,
    PushInstruction,
    WaitInstruction,
)

_JMP_CONDITIONS = ["", "!x", "x--", "!y", "y--", "x!=y", "pin", "!osre"]
_IN_SOURCES = ["pins", "x", "y", "null", None, None, "isr", "osr"]
_OUT_DESTS = ["pins", "x", "y", "null", "pindirs", "pc", "isr", "exec"]
_MOV_SOURCES = ["pins", "x", "y", "null", None, "status", "isr", "osr"]
_MOV_DESTS = ["pins", "x", "y", "null", None, "pc", "isr", "osr"]
_WAIT_SOURCES = ["gpio", "pin", "irq"]
_SET_DESTS = ["pins", "x", "y", None, "pindirs"]


def _format_jmp(instr: JmpInstruction) -> str:
    parts = ["jmp"]
    condition = _JMP_CONDITIONS[instr.condition]
    if condition:
        parts.append(condition)
    parts.append(str(instr.target_address))
    return " ".join(parts)


def _format_wait(instr: WaitInstruction) -> str:
    source = _WAIT_SOURCES[instr.source]
    polarity = 1 if instr.polarity else 0
    if instr.source == 2:  # IRQ: bit 4 is REL, bits [3:0] are the IRQ number
        rel = bool(instr.index & 0x10)
        index = instr.index & 0x0F
        parts = ["wait", str(polarity), source, str(index)]
        if rel:
            parts.append("rel")
    else:
        parts = ["wait", str(polarity), source, str(instr.index)]
    return " ".join(parts)


def _format_in(instr: InInstruction) -> str:
    source = _IN_SOURCES[instr.source]
    return f"in {source}, {instr.bit_count}"


def _format_out(instr: OutInstruction) -> str:
    dest = _OUT_DESTS[instr.destination]
    return f"out {dest}, {instr.bit_count}"


def _format_push(instr: PushInstruction) -> str:
    parts = ["push"]
    if instr.if_full:
        parts.append("iffull")
    parts.append("block" if instr.block else "noblock")
    return " ".join(parts)


def _format_pull(instr: PullInstruction) -> str:
    parts = ["pull"]
    if instr.if_empty:
        parts.append("ifempty")
    parts.append("block" if instr.block else "noblock")
    return " ".join(parts)


def _format_irq(instr: IrqInstruction) -> str:
    if instr.clear:
        action = "clear"
    elif instr.wait:
        action = "wait"
    else:
        action = "set"
    parts = ["irq", action, str(instr.index)]
    if instr.idx_mode == 2:
        parts.append("rel")
    return " ".join(parts)


def _format_mov(opcode: int) -> str:
    source = opcode & 0x07
    operation = (opcode >> 3) & 0x03
    destination = (opcode >> 5) & 0x07

    dest_name = _MOV_DESTS[destination]
    src_name = _MOV_SOURCES[source]

    if destination == 2 and operation == 0 and source == 2:
        return "nop"

    op_prefix = "~" if operation == 1 else ""
    return f"mov {dest_name}, {op_prefix}{src_name}"


def _format_set(opcode: int) -> str:
    destination = (opcode >> 5) & 0x07
    value = opcode & 0x1F
    dest_name = _SET_DESTS[destination]
    return f"set {dest_name}, {value}"


def _format_suffix(opcode: int, side_set_count: int) -> str:
    bits_for_delay = 5 - side_set_count
    delay_mask = (1 << bits_for_delay) - 1
    delay_and_side = (opcode >> 8) & 0x1F
    delay = delay_and_side & delay_mask
    side = delay_and_side >> bits_for_delay

    parts = []
    if side_set_count > 0 and side != 0:
        parts.append(f" side {side}")
    if delay > 0:
        parts.append(f" [{delay}]")
    return "".join(parts)


_FORMATTERS = {
    JmpInstruction: _format_jmp,
    WaitInstruction: _format_wait,
    InInstruction: _format_in,
    OutInstruction: _format_out,
    PushInstruction: _format_push,
    PullInstruction: _format_pull,
    IrqInstruction: _format_irq,
}


def _format_instruction(instruction) -> str:
    formatter = _FORMATTERS.get(type(instruction))
    if formatter is None:
        raise ValueError(f"Unknown instruction type: {type(instruction)}")
    return formatter(instruction)


def disassemble(opcode: int, side_set_count: int = 0) -> str:
    """
    Disassemble a PIO opcode into a human-readable assembly string.

    Parameters
    ----------
    opcode : int
        The 16-bit PIO opcode to disassemble.
    side_set_count : int
        Number of bits used for side-set (0-5). Affects delay/side-set
        decoding.

    Returns
    -------
    str
        The assembly string, e.g. ``"jmp x-- 3 side 1 [2]"``.

    Raises
    ------
    ValueError
        If the opcode cannot be decoded.
    """
    decoder = InstructionDecoder(side_set_count=side_set_count)
    instruction = decoder.decode(opcode)

    if instruction is not None:
        body = _format_instruction(instruction)
    else:
        instruction_code = (opcode >> 13) & 7
        if instruction_code == 5:
            body = _format_mov(opcode)
        elif instruction_code == 7:
            body = _format_set(opcode)
        else:
            raise ValueError(f"Cannot disassemble opcode 0x{opcode:04X}")

    suffix = _format_suffix(opcode, side_set_count)
    return f"{body}{suffix}"
