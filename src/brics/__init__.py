# brics - main function and CLI argument parsing.
#
# Author: Jahin Z. <jahinzee>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#

__package__ = "brics"

from brics import exceptions as exc
from brics.compiler import compile_to_c
from brics.disassembler import disassemble
from brics.process import run_program
from brics.program import Program
from brics.relex import Relex

from argparse import ArgumentParser, Namespace, FileType
from typing import NoReturn, Optional

import sys


def _get_args() -> Namespace:
    """Parse command-line arguments."""
    # fmt: off
    p = ArgumentParser(
        "brics",
        description="A Brainfuck interpreter, disassembler and transpiler.")

    sub = p.add_subparsers(dest='subcommand')

    sub.add_parser(
        'run',
        help="execute program")

    sub_disassemble = sub.add_parser(
        'disassemble',
        help="output program into human readable form")

    sub_disassemble.add_argument(
        "-j", "--json",
        help="output disassembly as a JSON object.",
        action='store_true')

    sub.add_parser(
        'compile',
        help="compile program to C")

    p.add_argument(
        "FILE",
        type=FileType('r'),
        help="the Brainfuck source file")

    p.add_argument(
        "-x", "--relex",
        help=("a .brelex file for relex definitions "
              "(if unspecified, the standard Brainfuck instruction set will be used)"),
        nargs="?",
        type=FileType('r'),
        default=None)

    p.add_argument(
        "-o", "--optimise",
        help="optimise application code before continuing",
        action="store_true")

    # fmt: on
    return p.parse_args()


def _fatal_error(message: str, err: Optional[Exception] = None) -> NoReturn:
    print(f"{__package__}: {message}", file=sys.stderr)
    if err is not None:
        print(f"  {err}", file=sys.stderr)
    exit(1)


def main():
    args = _get_args()
    try:
        relex = Relex.from_relex_file(args.relex) if args.relex is not None else Relex.standard()
        program = Program(args.FILE, relex, optimise=args.optimise)

        match args.subcommand:
            case "run":
                run_program(program)
            case "disassemble":
                disassemble(program, to_json=args.json)
            case "compile":
                compile_to_c(program)
            case _:
                assert False, "unreachable"

    except (KeyboardInterrupt, exc.BfRuntimeGracefulExit):
        pass

    except exc.ParsingError as err:
        _fatal_error(f"cannot parse program file {args.FILE.name} at instruction {err.char}", err)

    except exc.RelexParsingError as err:
        _at_line = f" at line {err.line}" if err.line is not None else ""
        _fatal_error(f"cannot parse relex file {args.relex.name}{_at_line}", err)

    except BrokenPipeError:
        _fatal_error("broken pipe error")


if __name__ == "__main__":
    main()
