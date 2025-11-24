# brics - disassembly functionality.
#
# Author: Jahin Z. <jahinzee>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#

__package__ = "brics"

from brics.program import Program
from brics.instructions import Instruction

from math import log10
from typing import Iterable

import sys
import json

# region private


def _get_max_width(source: Iterable[int]) -> int:
    return int(log10(max(source))) + 1


# endregion


def _disassemble_json(program: Program):
    """
    Print a JSON disassembled form of the Brainfuck source code.
    """
    obj = {
        "filename": str(program.source_file),
        "optimised": program.optimised,
        "relex": program.relex.name,
        "instruction": [
            {"index": idx, "instruction": instr.name}
            for (idx, instr) in enumerate(program.instructions)
            if instr is not None
        ],
        "loop_indices": [{"left": li, "right": ri} for li, ri in sorted(program.loop_boundaries)],
    }
    json.dump(obj, sys.stdout, indent=2)


def _disassemble_readable(program: Program):
    """
    Print a human-readable disassembled form of the Brainfuck source code.

    EXAMPLE: A program "++++[--[-]]." will output to:
        ---
        == Disassembly for <filename>.b ==

        Optimised:  False
        Relex:      standard

        Instructions:
            0  Add
            1  Add
            2  Add
            3  Add
            4  BeginLoop
            5    Subtract
            6    Subtract
            7    BeginLoop
            8      Subtract
            9    EndLoop
            10  EndLoop
            11  Output
            12  ◻

        Loop Indices:
            4  10
            7  9
        ---
    """
    buf = sys.stdout

    print(f"== Disassembly for {program.source_file} ==\n\n", end="")

    buf.write(f"Optimised:  {program.optimised}\n")
    buf.write(f"Relex:      {program.relex.name}\n\n")

    buf.write("Instructions:\n")

    max_idx = _get_max_width((len(program.instructions),))
    indent_level = 0

    for idx, instr in enumerate(program.instructions):
        indent_level -= 1 if instr == Instruction.EndLoop else 0

        instr_name = "◻" if instr is None else instr.name
        buf.write(f"    {idx:>{max_idx}}  {'  ' * indent_level}{instr_name:<18}\n")

        indent_level += 1 if instr == Instruction.BeginLoop else 0

    buf.write(("\nLoop Indices:\n"))

    if len(program.loop_boundaries) == 0:
        buf.write("    (none)\n")
    else:
        max_li, max_ri = tuple(_get_max_width(i) for i in zip(*program.loop_boundaries))
        for li, ri in sorted(program.loop_boundaries):
            buf.write(f"    {li:>{max_li}} ⋄ {ri:<{max_ri}}\n")


def disassemble(program: Program, *, to_json: bool):
    if to_json:
        _disassemble_json(program)
    else:
        _disassemble_readable(program)
