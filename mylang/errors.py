"""
Structured error types with source code location and context formatting.
"""

from typing import Optional


class MyLangError(Exception):
    """Base error class for all MyLang errors."""

    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None, source: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.source = source

    def format(self, filename: str = "<source>") -> str:
        """Render a formatted, user-friendly error with snippet and caret pointer."""
        lines = [f"{self.__class__.__name__}: {self.message}"]
        if self.line is not None and self.column is not None:
            lines.append(f"  --> {filename}:{self.line}:{self.column}")
            if self.source:
                src_lines = self.source.splitlines()
                if 1 <= self.line <= len(src_lines):
                    error_line = src_lines[self.line - 1]
                    prefix = f" {self.line:4d} | "
                    lines.append(prefix + error_line)
                    indent = " " * (len(prefix) + max(0, self.column - 1))
                    lines.append(indent + "^")
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.format()


class LexerError(MyLangError):
    """Raised during tokenization."""
    pass


class ParseError(MyLangError):
    """Raised during syntactic parsing."""
    pass


class RuntimeError(MyLangError):
    """Raised during evaluation / execution."""
    pass


# Internal control flow signals (not exposed as user errors)
class ReturnSignal(Exception):
    """Signal used by the evaluator to unwind the stack on `return`."""
    def __init__(self, value: object = None):
        self.value = value


class BreakSignal(Exception):
    """Signal used to break out of loops."""
    pass


class ContinueSignal(Exception):
    """Signal used to jump to the next iteration of loops."""
    pass
