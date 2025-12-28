# brics - C compilation functionality.
#
# Author: Jahin Z. <jahinzee>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# A section of this file is licensed under Creative Commons Attribution-ShareAlike 2.5 Generic.
# See: https://creativecommons.org/licenses/by-sa/2.5/deed.en
#

__package__ = "brics"

from brics.instructions import Instruction
from brics.program import Program

import sys

# region private


def _instr_to_c_statement(instr: Instruction) -> str:
    """
    Returns a string containing a C statement for the given instruction, with the given
    identifier context.
    """
    match instr:
        case Instruction.Next:
            # Modular expression adapted from: https://stackoverflow.com/a/1082938
            # (ShreevatsaR, CC BY-SA 2.5)
            #
            # NOTE: using `+1`/`-1` instead of pre-increment to avoid compiler warnings,
            #       specifically, clang's `-Wunsequenced`.
            #
            return "ptr=((ptr+1)%30000+30000)%30000;"
        case Instruction.Previous:
            return "ptr=((ptr-1)%30000+30000)%30000;"
        case Instruction.Add:
            return "mem[ptr]++;"
        case Instruction.Subtract:
            return "mem[ptr]--;"
        case Instruction.Input:
            return "mem[ptr]=getchar();"
        case Instruction.Output:
            return "putchar(mem[ptr]);"
        case Instruction.BeginLoop:
            return "while(mem[ptr]){"
        case Instruction.EndLoop:
            return "};"


# endregion


def compile_to_c(program: Program):
    """
    Converts the given Program to C code using the given relex, and prints to standard output.

    Uses `source_filename`, `optimised` and `Relex` for header and context comments.
    """
    buf = sys.stdout

    # Writing: comment header - program source and optimisation context
    #
    buf.write((
        "/* \n"
        " * Code auto-generated with brics.\n"
       f" *   Source file: {program.source_file}\n"
       f" *   Optimised:   {program.optimised}\n"
       f" *   Relex:       {program.relex.name}\n"
        " */\n"))  # fmt: skip

    # Writing: code preamble
    #
    buf.write((
        "#include <stdio.h>\n"
        "int main(void){"
            "char mem[30000];"
            "int ptr=0;"))  # fmt: skip

    for instr in program.instructions:
        # Writing: current instruction
        #
        buf.write(_instr_to_c_statement(instr))

    # Writing: code epilogue
    #   * end main function
    #
    buf.write("}\n")
