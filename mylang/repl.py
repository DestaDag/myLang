"""
Interactive Read-Eval-Print Loop (REPL) and file runner for MyLang.
"""

import sys
from typing import Optional
from mylang.ast import ExpressionStmt, Program
from mylang.environment import Environment
from mylang.errors import MyLangError
from mylang.evaluator import Evaluator
from mylang.lexer import Lexer
from mylang.parser import Parser
from mylang.values import stringify


def run_file(filepath: str) -> None:
    """Read and execute a MyLang source file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    except IOError as err:
        print(f"Error reading '{filepath}': {err}", file=sys.stderr)
        sys.exit(1)

    try:
        lexer = Lexer(source, filename=filepath)
        tokens = lexer.tokenize()

        parser = Parser(tokens, source=source)
        ast = parser.parse()

        evaluator = Evaluator(source=source)
        evaluator.evaluate(ast)
    except MyLangError as err:
        print(err.format(filename=filepath), file=sys.stderr)
        sys.exit(1)


def count_delimiters(line: str) -> int:
    """Helper to detect unclosed braces/brackets/parentheses."""
    balance = 0
    in_string = False
    quote_char = ""
    i = 0
    while i < len(line):
        ch = line[i]
        if in_string:
            if ch == "\\" and i + 1 < len(line):
                i += 2
                continue
            if ch == quote_char:
                in_string = False
        else:
            if ch in ('"', "'"):
                in_string = True
                quote_char = ch
            elif ch in ("{", "(", "["):
                balance += 1
            elif ch in ("}", ")", "]"):
                balance -= 1
            elif ch == "/" and i + 1 < len(line) and line[i + 1] == "/":
                break  # comment till end of line
        i += 1
    return balance


def start_repl() -> None:
    """Start an interactive session with persistent environment."""
    from mylang import __version__

    print(f"MyLang v{__version__} Interactive Shell")
    print("Type ':help' for commands, ':exit' or Ctrl+D to quit.\n")

    evaluator = Evaluator()
    buffer: list[str] = []
    delimiter_depth = 0

    while True:
        try:
            prompt = "... " if buffer else ">>> "
            line = input(prompt)

            # Check special repl commands only if not inside a multi-line buffer
            if not buffer and line.strip().startswith(":"):
                cmd = line.strip()
                if cmd in (":exit", ":quit", ":q"):
                    print("Goodbye!")
                    break
                elif cmd == ":help":
                    print("REPL Commands:")
                    print("  :help          Show this help message")
                    print("  :env           List variables in current global scope")
                    print("  :tokens <code> Show lexer tokens for given code")
                    print("  :ast <code>    Show parsed AST structure for given code")
                    print("  :exit / :q     Exit the REPL")
                    continue
                elif cmd == ":env":
                    print("Global Environment:")
                    for k, v in evaluator.globals.values.items():
                        kind = "const" if k in evaluator.globals.constants else "var"
                        print(f"  [{kind}] {k} = {stringify(v)}")
                    continue
                elif cmd.startswith(":tokens "):
                    code = cmd[8:]
                    try:
                        tokens = Lexer(code).tokenize()
                        for tok in tokens:
                            print(f"  {tok}")
                    except MyLangError as e:
                        print(e.format())
                    continue
                elif cmd.startswith(":ast "):
                    code = cmd[5:]
                    try:
                        toks = Lexer(code).tokenize()
                        ast = Parser(toks, source=code).parse()
                        print(f"  {ast}")
                    except MyLangError as e:
                        print(e.format())
                    continue
                else:
                    print(f"Unknown command '{cmd}'. Type ':help' for options.")
                    continue

            buffer.append(line)
            delimiter_depth += count_delimiters(line)

            if delimiter_depth > 0:
                continue

            # Process completed buffer
            source = "\n".join(buffer)
            buffer.clear()
            delimiter_depth = 0

            if not source.strip():
                continue

            try:
                evaluator.source = source
                tokens = Lexer(source).tokenize()
                parser = Parser(tokens, source=source)
                program = parser.parse()

                # If single expression statement, print its evaluated value
                if (
                    len(program.statements) == 1
                    and isinstance(program.statements[0], ExpressionStmt)
                ):
                    val = evaluator.evaluate(program.statements[0])
                    if val is not None:
                        print(stringify(val))
                else:
                    evaluator.evaluate(program)

            except MyLangError as err:
                print(err.format(), file=sys.stderr)

        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
