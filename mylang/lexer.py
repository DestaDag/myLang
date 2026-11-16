"""
Lexical analyzer (tokenizer) for MyLang.
"""

from typing import List, Optional
from mylang.errors import LexerError
from mylang.tokens import KEYWORDS, SourceLocation, Token, TokenType


class Lexer:
    """
    Transforms raw source code into a stream of Token objects.
    Tracks line and column numbers for precise error reporting.
    """

    def __init__(self, source: str, filename: str = "<stdin>"):
        self.source = source
        self.filename = filename
        self.length = len(source)

        self.index = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> List[Token]:
        """Tokenize the entire source string and return a list of Tokens ending with EOF."""
        tokens: List[Token] = []

        while not self._is_at_end():
            self._skip_whitespace_and_comments()
            if self._is_at_end():
                break

            token = self._next_token()
            if token:
                tokens.append(token)

        tokens.append(
            Token(
                type=TokenType.EOF,
                value=None,
                location=SourceLocation(self.line, self.column, self.filename),
            )
        )
        return tokens

    # --- Character Navigation Helpers ---

    def _is_at_end(self) -> bool:
        return self.index >= self.length

    def _peek(self, offset: int = 0) -> str:
        pos = self.index + offset
        if pos >= self.length:
            return "\0"
        return self.source[pos]

    def _advance(self) -> str:
        ch = self.source[self.index]
        self.index += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _match(self, expected: str) -> bool:
        if self._is_at_end() or self.source[self.index] != expected:
            return False
        self._advance()
        return True

    # --- Whitespace and Comments ---

    def _skip_whitespace_and_comments(self) -> None:
        while not self._is_at_end():
            ch = self._peek()

            if ch in (" ", "\t", "\r", "\n"):
                self._advance()
            elif ch == "/" and self._peek(1) == "/":
                # Single-line comment
                while not self._is_at_end() and self._peek() != "\n":
                    self._advance()
            elif ch == "/" and self._peek(1) == "*":
                # Multi-line comment
                start_line = self.line
                start_col = self.column
                self._advance()  # /
                self._advance()  # *
                closed = False
                while not self._is_at_end():
                    if self._peek() == "*" and self._peek(1) == "/":
                        self._advance()  # *
                        self._advance()  # /
                        closed = True
                        break
                    self._advance()
                if not closed:
                    raise LexerError(
                        "Unterminated multi-line comment",
                        line=start_line,
                        column=start_col,
                        source=self.source,
                    )
            else:
                break

    # --- Token Extraction ---

    def _next_token(self) -> Optional[Token]:
        start_line = self.line
        start_col = self.column
        loc = SourceLocation(start_line, start_col, self.filename)

        ch = self._advance()

        # 1-character and 2-character operators
        if ch == "+":
            if self._match("="):
                return Token(TokenType.PLUS_EQUAL, "+=", loc)
            return Token(TokenType.PLUS, "+", loc)
        if ch == "-":
            if self._match("="):
                return Token(TokenType.MINUS_EQUAL, "-=", loc)
            return Token(TokenType.MINUS, "-", loc)
        if ch == "*":
            if self._match("="):
                return Token(TokenType.STAR_EQUAL, "*=", loc)
            return Token(TokenType.STAR, "*", loc)
        if ch == "/":
            if self._match("="):
                return Token(TokenType.SLASH_EQUAL, "/=", loc)
            return Token(TokenType.SLASH, "/", loc)
        if ch == "%":
            return Token(TokenType.PERCENT, "%", loc)
        if ch == "^":
            return Token(TokenType.CARET, "^", loc)

        if ch == "=":
            if self._match("="):
                return Token(TokenType.EQUAL_EQUAL, "==", loc)
            return Token(TokenType.EQUAL, "=", loc)
        if ch == "!":
            if self._match("="):
                return Token(TokenType.BANG_EQUAL, "!=", loc)
            return Token(TokenType.BANG, "!", loc)
        if ch == "<":
            if self._match("="):
                return Token(TokenType.LESS_EQUAL, "<=", loc)
            return Token(TokenType.LESS, "<", loc)
        if ch == ">":
            if self._match("="):
                return Token(TokenType.GREATER_EQUAL, ">=", loc)
            return Token(TokenType.GREATER, ">", loc)

        # Logical symbols support: && and ||
        if ch == "&" and self._match("&"):
            return Token(TokenType.AND, "and", loc)
        if ch == "|" and self._match("|"):
            return Token(TokenType.OR, "or", loc)

        # Delimiters
        if ch == "(":
            return Token(TokenType.LPAREN, "(", loc)
        if ch == ")":
            return Token(TokenType.RPAREN, ")", loc)
        if ch == "{":
            return Token(TokenType.LBRACE, "{", loc)
        if ch == "}":
            return Token(TokenType.RBRACE, "}", loc)
        if ch == "[":
            return Token(TokenType.LBRACKET, "[", loc)
        if ch == "]":
            return Token(TokenType.RBRACKET, "]", loc)
        if ch == ",":
            return Token(TokenType.COMMA, ",", loc)
        if ch == ";":
            return Token(TokenType.SEMICOLON, ";", loc)
        if ch == ":":
            return Token(TokenType.COLON, ":", loc)
        if ch == ".":
            return Token(TokenType.DOT, ".", loc)

        # String literals
        if ch in ('"', "'"):
            return self._scan_string(ch, loc)

        # Number literals
        if ch.isdigit():
            return self._scan_number(ch, loc)

        # Identifiers and keywords
        if ch.isalpha() or ch == "_":
            return self._scan_identifier(ch, loc)

        raise LexerError(
            f"Unexpected character: {ch!r}",
            line=start_line,
            column=start_col,
            source=self.source,
        )

    def _scan_string(self, quote_char: str, loc: SourceLocation) -> Token:
        chars: List[str] = []
        while not self._is_at_end() and self._peek() != quote_char:
            ch = self._advance()
            if ch == "\\":
                if self._is_at_end():
                    raise LexerError(
                        "Unfinished escape sequence at end of string",
                        line=self.line,
                        column=self.column,
                        source=self.source,
                    )
                escaped = self._advance()
                if escaped == "n":
                    chars.append("\n")
                elif escaped == "t":
                    chars.append("\t")
                elif escaped == "r":
                    chars.append("\r")
                elif escaped == "\\":
                    chars.append("\\")
                elif escaped == quote_char:
                    chars.append(quote_char)
                else:
                    chars.append(escaped)
            else:
                chars.append(ch)

        if self._is_at_end():
            raise LexerError(
                "Unterminated string literal",
                line=loc.line,
                column=loc.column,
                source=self.source,
            )

        self._advance()  # Consume closing quote
        return Token(TokenType.STRING, "".join(chars), loc)

    def _scan_number(self, first_digit: str, loc: SourceLocation) -> Token:
        digits = [first_digit]
        is_float = False

        while self._peek().isdigit():
            digits.append(self._advance())

        # Check for fractional part
        if self._peek() == "." and self._peek(1).isdigit():
            is_float = True
            digits.append(self._advance())  # Consume '.'
            while self._peek().isdigit():
                digits.append(self._advance())

        # Scientific notation: e.g. 1e5 or 2.5e-3
        if self._peek() in ("e", "E"):
            is_float = True
            digits.append(self._advance())
            if self._peek() in ("+", "-"):
                digits.append(self._advance())
            if not self._peek().isdigit():
                raise LexerError(
                    "Malformed exponent in number literal",
                    line=self.line,
                    column=self.column,
                    source=self.source,
                )
            while self._peek().isdigit():
                digits.append(self._advance())

        raw_str = "".join(digits)
        value = float(raw_str) if is_float else int(raw_str)
        return Token(TokenType.NUMBER, value, loc)

    def _scan_identifier(self, first_char: str, loc: SourceLocation) -> Token:
        chars = [first_char]
        while self._peek().isalnum() or self._peek() == "_":
            chars.append(self._advance())

        ident = "".join(chars)
        token_type = KEYWORDS.get(ident, TokenType.IDENTIFIER)
        return Token(token_type, ident, loc)
