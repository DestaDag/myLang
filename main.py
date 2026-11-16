#!/usr/bin/env python3
"""
MyLang CLI entry point.
Run without arguments to enter the interactive REPL,
or pass a file path to execute a script.
"""

import sys
from mylang.repl import run_file, start_repl


def main() -> None:
    if len(sys.argv) > 1:
        if sys.argv[1] in ("-h", "--help"):
            print("Usage:")
            print("  python3 main.py          Start the interactive REPL")
            print("  python3 main.py <file>   Execute a MyLang source file (.ml)")
            sys.exit(0)
        run_file(sys.argv[1])
    else:
        start_repl()


if __name__ == "__main__":
    main()
