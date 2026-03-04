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
import pytest
from pioemu import disassemble


@pytest.mark.parametrize(
    "opcode, side_set_count, expected",
    [
        # JMP
        pytest.param(0x0000, 0, "jmp 0", id="jmp always 0"),
        pytest.param(0x001F, 0, "jmp 31", id="jmp always 31"),
        pytest.param(0x0020, 0, "jmp !x 0", id="jmp !x 0"),
        pytest.param(0x0040, 0, "jmp x-- 0", id="jmp x-- 0"),
        pytest.param(0x0060, 0, "jmp !y 0", id="jmp !y 0"),
        pytest.param(0x0080, 0, "jmp y-- 0", id="jmp y-- 0"),
        pytest.param(0x00A0, 0, "jmp x!=y 0", id="jmp x!=y 0"),
        pytest.param(0x00C0, 0, "jmp pin 0", id="jmp pin 0"),
        pytest.param(0x00E0, 0, "jmp !osre 0", id="jmp !osre 0"),
        # WAIT
        pytest.param(0x2000, 0, "wait 0 gpio 0", id="wait 0 gpio 0"),
        pytest.param(0x2080, 0, "wait 1 gpio 0", id="wait 1 gpio 0"),
        pytest.param(0x2020, 0, "wait 0 pin 0", id="wait 0 pin 0"),
        pytest.param(0x20A0, 0, "wait 1 pin 0", id="wait 1 pin 0"),
        pytest.param(0x2040, 0, "wait 0 irq 0", id="wait 0 irq 0"),
        pytest.param(0x20C0, 0, "wait 1 irq 0", id="wait 1 irq 0"),
        pytest.param(0x2050, 0, "wait 0 irq 0 rel", id="wait 0 irq 0 rel"),
        pytest.param(0x20D0, 0, "wait 1 irq 0 rel", id="wait 1 irq 0 rel"),
        # IN
        pytest.param(0x4001, 0, "in pins, 1", id="in pins, 1"),
        pytest.param(0x4021, 0, "in x, 1", id="in x, 1"),
        pytest.param(0x4041, 0, "in y, 1", id="in y, 1"),
        pytest.param(0x4061, 0, "in null, 1", id="in null, 1"),
        pytest.param(0x40C1, 0, "in isr, 1", id="in isr, 1"),
        pytest.param(0x40E1, 0, "in osr, 1", id="in osr, 1"),
        pytest.param(0x4000, 0, "in pins, 32", id="in pins, 32"),
        # OUT
        pytest.param(0x6001, 0, "out pins, 1", id="out pins, 1"),
        pytest.param(0x6021, 0, "out x, 1", id="out x, 1"),
        pytest.param(0x6041, 0, "out y, 1", id="out y, 1"),
        pytest.param(0x6061, 0, "out null, 1", id="out null, 1"),
        pytest.param(0x6081, 0, "out pindirs, 1", id="out pindirs, 1"),
        pytest.param(0x60A1, 0, "out pc, 1", id="out pc, 1"),
        pytest.param(0x60C1, 0, "out isr, 1", id="out isr, 1"),
        pytest.param(0x6000, 0, "out pins, 32", id="out pins, 32"),
        # PUSH
        pytest.param(0x8000, 0, "push noblock", id="push noblock"),
        pytest.param(0x8020, 0, "push block", id="push block"),
        pytest.param(0x8040, 0, "push iffull noblock", id="push iffull noblock"),
        pytest.param(0x8060, 0, "push iffull block", id="push iffull block"),
        # PULL
        pytest.param(0x8080, 0, "pull noblock", id="pull noblock"),
        pytest.param(0x80A0, 0, "pull block", id="pull block"),
        pytest.param(0x80C0, 0, "pull ifempty noblock", id="pull ifempty noblock"),  # noqa: E501
        pytest.param(0x80E0, 0, "pull ifempty block", id="pull ifempty block"),
        # MOV
        pytest.param(0xA000, 0, "mov pins, pins", id="mov pins, pins"),
        pytest.param(0xA001, 0, "mov pins, x", id="mov pins, x"),
        pytest.param(0xA002, 0, "mov pins, y", id="mov pins, y"),
        pytest.param(0xA003, 0, "mov pins, null", id="mov pins, null"),
        pytest.param(0xA006, 0, "mov pins, isr", id="mov pins, isr"),
        pytest.param(0xA007, 0, "mov pins, osr", id="mov pins, osr"),
        pytest.param(0xA020, 0, "mov x, pins", id="mov x, pins"),
        pytest.param(0xA02F, 0, "mov x, ~osr", id="mov x, ~osr"),
        pytest.param(0xA0C5, 0, "mov isr, status", id="mov isr, status"),
        pytest.param(0xA0E1, 0, "mov osr, x", id="mov osr, x"),
        # NOP
        pytest.param(0xA042, 0, "nop", id="nop"),
        # IRQ
        pytest.param(0xC000, 0, "irq set 0", id="irq set 0"),
        pytest.param(0xC002, 0, "irq set 2", id="irq set 2"),
        pytest.param(0xC020, 0, "irq wait 0", id="irq wait 0"),
        pytest.param(0xC040, 0, "irq clear 0", id="irq clear 0"),
        pytest.param(0xC043, 0, "irq clear 3", id="irq clear 3"),
        pytest.param(0xC010, 0, "irq set 0 rel", id="irq set 0 rel"),
        pytest.param(0xC030, 0, "irq wait 0 rel", id="irq wait 0 rel"),
        # SET
        pytest.param(0xE000, 0, "set pins, 0", id="set pins, 0"),
        pytest.param(0xE001, 0, "set pins, 1", id="set pins, 1"),
        pytest.param(0xE01F, 0, "set pins, 31", id="set pins, 31"),
        pytest.param(0xE020, 0, "set x, 0", id="set x, 0"),
        pytest.param(0xE03F, 0, "set x, 31", id="set x, 31"),
        pytest.param(0xE040, 0, "set y, 0", id="set y, 0"),
        pytest.param(0xE042, 0, "set y, 2", id="set y, 2"),
        pytest.param(0xE081, 0, "set pindirs, 1", id="set pindirs, 1"),
        # Delay suffix
        pytest.param(0x0F00, 0, "jmp 0 [15]", id="jmp 0 with max delay"),
        pytest.param(0x0100, 0, "jmp 0 [1]", id="jmp 0 with delay 1"),
        # Side-set suffix
        pytest.param(0x1000, 1, "jmp 0 side 1", id="jmp 0 side 1"),
        pytest.param(0x0900, 2, "jmp 0 side 1 [1]", id="jmp 0 side 1 [1]"),
        pytest.param(0x1800, 2, "jmp 0 side 3", id="jmp 0 side 3"),
    ],
)
def test_disassemble(opcode: int, side_set_count: int, expected: str):
    assert disassemble(opcode, side_set_count) == expected
