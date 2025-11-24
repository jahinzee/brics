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
            # NOTE: using `+1`/`-1` instead of pre-increment to avoid compiler warnings,
            #       specifically, clang's `-Wunsequenced`.
            #
            return "ptr = MOD(ptr + 1, MEMORY_LENGTH);"
        case Instruction.Previous:
            return "ptr = MOD(ptr - 1, MEMORY_LENGTH);"
        case Instruction.Add:
            return "mem[ptr]++;"
        case Instruction.Subtract:
            return "mem[ptr]--;"
        case Instruction.Input:
            return "mem[ptr] = getchar();"
        case Instruction.Output:
            return "putchar(mem[ptr]);"
        case Instruction.BeginLoop:
            return "while (mem[ptr]) {"
        case Instruction.EndLoop:
            return "};"


# endregion


def compile_to_c(program: Program):
    """
    Converts the given Program to C code using the given relex, and prints to standard output.

    Uses `source_filename`, `optimised` and `Relex` for header and context comments.
    """
    buf = sys.stdout

    # fmt: off

    # Writing: Comment header:
    #   * program source and optimisation context
    #
    buf.write((
        "/* \n"
        " * Code auto-generated with brics.\n"
       f" *   Source file: {program.source_file}\n"
       f" *   Optimised:   {program.optimised}\n"
       f" *   Relex:       {program.relex.name}\n"
        " */\n"
        "\n"))

    # Writing: Code header:
    #   * includes and macros for memory length and modulo operation 
    #   * main function init
    #   * memory and pointer init
    #
    buf.write((
        "#include <stdio.h>\n"
        "#define MEMORY_LENGTH 30000\n"
        "\n"
        # region cc-by-sa-2.5
        #   This section licensed under CC BY-SA 2.5.
        #   Based on code by ShreevatsaR.
        "/* MOD macro adapted from: https://stackoverflow.com/a/1082938 (ShreevatsaR, CC BY-SA 2.5) */\n"
        "#define MOD(a, b) (a % b + b) % b\n"
        # endregion
        "\n"
        "int main(void) {\n"
        "\n"
        "    /* (program init) */\n"
        "    char mem[MEMORY_LENGTH];\n"
        "    int ptr = 0;\n"
        "    \n"))
    # fmt: on

    indent_level = 0

    for instr in program.instructions:
        if instr is None:
            continue

        indent_level -= 1 if instr == Instruction.EndLoop else 0

        # Writing: Current instruction:
        #   * context comment
        #   * adjust indentation when needed
        #
        indent = "    " * (indent_level + 1)
        # fmt: off
        buf.write((
           f"{indent}/* {f'(instr {instr.name})'} */\n"
           f"{indent}{_instr_to_c_statement(instr)}\n"
            "\n"))
        # fmt: on

        indent_level += 1 if instr == Instruction.BeginLoop else 0

    # Writing: Code footer:
    #   * end main function
    #
    buf.write("}")
