"""
Token definitions and source tracking for MyLang.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional


class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()

    # Keywords
    VAR = auto()
    CONST = auto()
    FUNC = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    TO = auto()
    BY = auto()
    BREAK = auto()
    CONTINUE = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # Arithmetic & Operators
    PLUS = auto()         # +
    MINUS = auto()        # -
    STAR = auto()         # *
    SLASH = auto()        # /
    PERCENT = auto()      # %
    CARET = auto()        # ^ (exponentiation)
    
    # Assignment & Compound Assignment
    EQUAL = auto()        # =
    PLUS_EQUAL = auto()   # +=
    MINUS_EQUAL = auto()  # -=
    STAR_EQUAL = auto()   # *=
    SLASH_EQUAL = auto()  # /=

    # Comparison & Equality
    EQUAL_EQUAL = auto()  # ==
    BANG_EQUAL = auto()   # !=
    LESS = auto()         # <
    LESS_EQUAL = auto()   # <=
    GREATER = auto()      # >
    GREATER_EQUAL = auto()# >=
    BANG = auto()         # !

    # Delimiters
    LPAREN = auto()       # (
    RPAREN = auto()       # )
    LBRACE = auto()       # {
    RBRACE = auto()       # }
    LBRACKET = auto()     # [
    RBRACKET = auto()     # ]
    COMMA = auto()        # ,
    SEMICOLON = auto()    # ;
    COLON = auto()        # :
    DOT = auto()          # .

    # End of File
    EOF = auto()


KEYWORDS: dict[str, TokenType] = {
    "var": TokenType.VAR,
    "const": TokenType.CONST,
    "func": TokenType.FUNC,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "to": TokenType.TO,
    "by": TokenType.BY,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "null": TokenType.NULL,
    "nil": TokenType.NULL,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
}


@dataclass(frozen=True)
class SourceLocation:
    line: int
    column: int
    filename: str = "<stdin>"

    def __str__(self) -> str:
        return f"{self.filename}:{self.line}:{self.column}"


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: Any
    location: SourceLocation

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, line={self.location.line}, col={self.location.column})"
