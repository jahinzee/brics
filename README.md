# brics

brics (*abbr.* "**b**rainfuck **r**elexer **i**nterpreter and **c**ompiler **s**uite") is a utility
for interpreting and compiling programs written in Brainfuck and its [relexes][esolang-tbs].

[esolang-tbs]: https://esolangs.org/wiki/Trivial_brainfuck_substitution

## Installation

This program uses [`uv`](https://docs.astral.sh/uv/) for packaging and development.

```sh
git clone https://github.com/jahinzee/brics
cd brics
uv install .
```

Alternatively, use [`pipx`](https://pipx.pypa.io/latest/) to install it as a globally available
executable:

```sh
pipx install git+https://github.com/jahinzee/brics
```

## Usage

### Running programs

At its core, brics functions as a Brainfuck interpreter. Use `brics run` to execute
a Brainfuck program:

**Input:** ([source](https://en.wikipedia.org/wiki/Brainfuck#Hello_World!); first one)

```sh
brics run helloworld.b
```

**Output:**
```
Hello World!
```

brics can also detect invalid Brainfuck programs. The only real way a string of characters can fail
to be a valid Brainfuck program is if it doesn't have matching square brackets.

**Input:** (source: `++++[-[-[-]].`)

```sh
brics run badbrackets.b
```

**Output:**

```
brics: cannot parse program file badbrackets.b at instruction 4:
  Unmatched [ instruction
```

### Optimisations

brics supports some basic optimisations. One that is always on by default is trimming of no-op
characters.

You can enable additional optimisations with `-o`/`--optimise` – currently only one extra
optimisation is supported: removing initial comment headers.

### Relexes

brics also supports most [trivial Brainfuck substitutions][esolang-tbs], or as brics refers to them
as, *Brainfuck relexes*.

Use the `-x`/`--relex` options to specify a relex file ([see below](#defining-a-relex)):

**Input:** ([source][Ook!]; Hello, world! program)

```sh
brics --relex Ook!.brelex run helloworld_Ook!.b
```

**Output:**

```
Hello World!
```

[Ook!]: https://esolangs.org/wiki/Ook!

#### Defining a relex

To execute a Brainfuck relex, a relex file must be provided. Here's an example relex file for the
[Ook!][] esolang by David Morgan-Mar: 

<p><details><summary><strong>File:</strong> Ook!.brelex </summary>

```
# Brainfuck relex file for Ook!
# Source: https://esolangs.org/wiki/Ook!
# 
# Any copyright is dedicated to the Public Domain.
# https://creativecommons.org/publicdomain/zero/1.0/
#

> Ook. Ook?
< Ook? Ook.
+ Ook. Ook.
- Ook! Ook!
. Ook! Ook.
, Ook. Ook!
[ Ook! Ook?
] Ook? Ook!
```

</details>
</p>


Each line in the relex file starts with the canonical Brainfuck instruction, followed by a space,
and then the substituted instruction. Blank lines and lines starting with a `#` are
ignored.

Note also that a relex must be exhaustive (i.e. all eight Brainfuck instructions must have a
substitution), and there may not be substitutions for characters that aren't Brainfuck instructions.

brics will reject invalid relex files.

**Input:** (with a half-defined brelex file)

```sh
brics --relex half.brelex run helloworld.b
```

**Output:**

```
brics: cannot parse relex file half.brelex:
  Relex definition is inexhaustive, missing instruction(s): ',', '-', '>', ']'
```

> [!WARNING]
> Substitutions that use only whitespace characters (such as a series of spaces) are not supported,
> they will probably not work or produce garbage results.

### Disassembly

brics can also disassemble a Brainfuck program into a human readable report form, or to JSON data.
Use `brics disassemble` for this.

You can use this for an algorithmic breakdown of the source into something more human readable,
or to compare optimisations.

**Input:** (source: `++++[--[-]].`)

```sh
brics disassemble test.b
```

<p><details><summary><strong>Output</strong></summary>


```
== Disassembly for test.b ==

Optimised:  False
Relex:      [standard]

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
    4 ⋄ 10
    7 ⋄ 9 
```

</details></p>

You can also export disassemblies to JSON:

**Input:** (source: `++++[--[-]].`)

```sh
brics disassemble --json test.b
```

<p><details><summary><strong>Output</strong></summary>

```json
{
  "filename": "test.b",
  "optimised": false,
  "relex": "[standard]",
  "instruction": [
    {
      "index": 0,
      "instruction": "Add"
    },
    {
      "index": 1,
      "instruction": "Add"
    },           
    // ...
  ],
  "loop_indices": [
    {
      "left": 4,
      "right": 10
    },
    {
      "left": 7,
      "right": 9
    }
  ]
}
```

</details></p>

brics can also disassemble with relexes – use the `-x`/`--relex` options *before* the `disassemble`
subcommand.

### Compilation (to C)

brics can compile Brainfuck programs (including relexes) into C code, using the `compile` command.

**Input:** ([source](https://en.wikipedia.org/wiki/Brainfuck#Hello_World!); first one)

```sh
brics compile helloworld.b
```

The C code is printed to standard output. You can save the code to a file with shell redirection,
or pipe it straight to a C compiler, such as `clang`:

**Input:**

```sh
brics compile helloworld.b | clang -x c -
./a.out
```

**Output:**

```
Hello World!
```

---

## License and Additional Notes

brics is [open source software][osd], and is overall licensed under the
[Mozilla Public License, v. 2.0][mpl-v-2.0], with some sections licensed under
[Creative Commons Attribution-ShareAlike 2.5 Generic][cc-by-sa-2.5].
See [LICENSE.txt](LICENSE.txt).

[osd]: https://opensource.org/osd
[mpl-v-2.0]: https://www.mozilla.org/en-US/MPL/2.0/
[cc-by-sa-2.5]: https://creativecommons.org/licenses/by-sa/2.5/deed.en

![brics is a Brainmade project.](https://brainmade.org/88x31-dark.png)

brics is a [Brainmade](https://brainmade.org/) project. None of the source code was written
with generative AI.