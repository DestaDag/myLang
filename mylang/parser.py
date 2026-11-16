"""
Recursive descent parser for MyLang.
Constructs an AST with full source location tracking.
"""

from typing import List, Optional
from mylang.ast import (
    AssignExpr,
    BinaryExpr,
    BlockStmt,
    BreakStmt,
    CallExpr,
    ContinueStmt,
    Expression,
    ExpressionStmt,
    ForStmt,
    FunctionExpr,
    FunctionStmt,
    IdentifierExpr,
    IfStmt,
    IndexExpr,
    ListExpr,
    LiteralExpr,
    LogicalExpr,
    Program,
    ReturnStmt,
    Statement,
    UnaryExpr,
    VarStmt,
    WhileStmt,
)
from mylang.errors import ParseError
from mylang.tokens import SourceLocation, Token, TokenType


class Parser:
    """
    Parses a sequence of tokens into an Abstract Syntax Tree (AST).
    Uses recursive descent with precedence climbing for expressions.
    """

    def __init__(self, tokens: List[Token], source: Optional[str] = None):
        self.tokens = tokens
        self.source = source
        self.current = 0

    def parse(self) -> Program:
        """Parse the complete token stream into a Program node."""
        statements: List[Statement] = []
        start_loc = self._peek().location

        while not self._is_at_end():
            stmt = self._declaration()
            if stmt:
                statements.append(stmt)

        return Program(location=start_loc, statements=statements)

    # --- Token Navigation ---

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self, offset: int = 0) -> Token:
        pos = self.current + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _consume(self, token_type: TokenType, error_message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        curr = self._peek()
        raise ParseError(
            f"{error_message} (found {curr.type.name} {curr.value!r})",
            line=curr.location.line,
            column=curr.location.column,
            source=self.source,
        )

    def _match_semicolon(self) -> None:
        """Allow optional semicolon before '}' or EOF, otherwise consume semicolon."""
        if self._match(TokenType.SEMICOLON):
            return
        if self._check(TokenType.RBRACE) or self._is_at_end():
            return
        curr = self._peek()
        raise ParseError(
            f"Expected ';' after statement (found {curr.type.name} {curr.value!r})",
            line=curr.location.line,
            column=curr.location.column,
            source=self.source,
        )

    # --- Declarations and Statements ---

    def _declaration(self) -> Statement:
        try:
            if self._match(TokenType.VAR):
                return self._var_declaration(is_const=False)
            if self._match(TokenType.CONST):
                return self._var_declaration(is_const=True)
            if self._match(TokenType.FUNC):
                # If followed by IDENTIFIER, it's a function declaration statement
                if self._check(TokenType.IDENTIFIER):
                    return self._function_declaration()
                # Otherwise, rewind and parse as expression statement (anonymous func)
                self.current -= 1
            return self._statement()
        except ParseError as err:
            self._synchronize()
            raise err

    def _var_declaration(self, is_const: bool) -> Statement:
        loc = self._previous().location
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected variable name")
        name = name_tok.value

        initializer: Optional[Expression] = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()
        elif is_const:
            raise ParseError(
                f"Constant '{name}' must be initialized upon declaration",
                line=name_tok.location.line,
                column=name_tok.location.column,
                source=self.source,
            )

        self._match_semicolon()
        return VarStmt(location=loc, name=name, initializer=initializer, is_const=is_const)

    def _function_declaration(self) -> Statement:
        loc = self._previous().location
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected function name")
        name = name_tok.value

        self._consume(TokenType.LPAREN, "Expected '(' after function name")
        params = self._parameters()
        self._consume(TokenType.RPAREN, "Expected ')' after parameters")

        self._consume(TokenType.LBRACE, "Expected '{' before function body")
        body = self._block_statement()
        return FunctionStmt(location=loc, name=name, params=params, body=body)

    def _parameters(self) -> List[str]:
        params: List[str] = []
        if not self._check(TokenType.RPAREN):
            param_tok = self._consume(TokenType.IDENTIFIER, "Expected parameter name")
            params.append(param_tok.value)
            while self._match(TokenType.COMMA):
                param_tok = self._consume(TokenType.IDENTIFIER, "Expected parameter name after ','")
                params.append(param_tok.value)
        return params

    def _statement(self) -> Statement:
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.RETURN):
            return self._return_statement()
        if self._match(TokenType.BREAK):
            loc = self._previous().location
            self._match_semicolon()
            return BreakStmt(location=loc)
        if self._match(TokenType.CONTINUE):
            loc = self._previous().location
            self._match_semicolon()
            return ContinueStmt(location=loc)
        if self._match(TokenType.LBRACE):
            return self._block_statement()

        return self._expression_statement()

    def _if_statement(self) -> Statement:
        loc = self._previous().location
        has_paren = self._match(TokenType.LPAREN)
        condition = self._expression()
        if has_paren:
            self._consume(TokenType.RPAREN, "Expected ')' after if condition")

        then_branch = self._statement()
        else_branch = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()

        return IfStmt(location=loc, condition=condition, then_branch=then_branch, else_branch=else_branch)

    def _while_statement(self) -> Statement:
        loc = self._previous().location
        has_paren = self._match(TokenType.LPAREN)
        condition = self._expression()
        if has_paren:
            self._consume(TokenType.RPAREN, "Expected ')' after while condition")

        body = self._statement()
        return WhileStmt(location=loc, condition=condition, body=body)

    def _for_statement(self) -> Statement:
        loc = self._previous().location
        has_paren = self._match(TokenType.LPAREN)

        # Allow optional 'var' keyword: for var i to n ...
        self._match(TokenType.VAR)

        var_tok = self._consume(TokenType.IDENTIFIER, "Expected variable name in for loop")
        var_name = var_tok.value

        # Optional initial value: for i = 0 to n
        start_expr: Optional[Expression] = None
        if self._match(TokenType.EQUAL):
            start_expr = self._expression()

        self._consume(TokenType.TO, "Expected 'to' in for loop")
        end_expr = self._expression()

        # Optional step: by x
        step_expr: Optional[Expression] = None
        if self._match(TokenType.BY):
            step_expr = self._expression()

        if has_paren:
            self._consume(TokenType.RPAREN, "Expected ')' after for loop clause")

        body = self._statement()
        return ForStmt(
            location=loc,
            var_name=var_name,
            start=start_expr,
            end=end_expr,
            step=step_expr,
            body=body,
        )

    def _return_statement(self) -> Statement:
        loc = self._previous().location
        value: Optional[Expression] = None
        if not self._check(TokenType.SEMICOLON) and not self._check(TokenType.RBRACE):
            value = self._expression()
        self._match_semicolon()
        return ReturnStmt(location=loc, value=value)

    def _block_statement(self) -> BlockStmt:
        loc = self._previous().location
        statements: List[Statement] = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            statements.append(self._declaration())
        self._consume(TokenType.RBRACE, "Expected '}' after block")
        return BlockStmt(location=loc, statements=statements)

    def _expression_statement(self) -> Statement:
        expr = self._expression()
        self._match_semicolon()
        return ExpressionStmt(location=expr.location, expression=expr)

    # --- Expressions ---

    def _expression(self) -> Expression:
        return self._assignment()

    def _assignment(self) -> Expression:
        expr = self._logical_or()

        if self._match(
            TokenType.EQUAL,
            TokenType.PLUS_EQUAL,
            TokenType.MINUS_EQUAL,
            TokenType.STAR_EQUAL,
            TokenType.SLASH_EQUAL,
        ):
            op_tok = self._previous()
            value = self._assignment()

            # Handle compound assignments: desugar to binary expression
            if op_tok.type != TokenType.EQUAL:
                op_map = {
                    TokenType.PLUS_EQUAL: TokenType.PLUS,
                    TokenType.MINUS_EQUAL: TokenType.MINUS,
                    TokenType.STAR_EQUAL: TokenType.STAR,
                    TokenType.SLASH_EQUAL: TokenType.SLASH,
                }
                value = BinaryExpr(
                    location=op_tok.location,
                    left=expr,
                    operator=op_map[op_tok.type],
                    right=value,
                )

            if isinstance(expr, (IdentifierExpr, IndexExpr)):
                return AssignExpr(location=op_tok.location, target=expr, value=value)

            raise ParseError(
                f"Invalid assignment target: {expr}",
                line=op_tok.location.line,
                column=op_tok.location.column,
                source=self.source,
            )

        return expr

    def _logical_or(self) -> Expression:
        expr = self._logical_and()
        while self._match(TokenType.OR):
            op = self._previous()
            right = self._logical_and()
            expr = LogicalExpr(location=op.location, left=expr, operator=op.type, right=right)
        return expr

    def _logical_and(self) -> Expression:
        expr = self._equality()
        while self._match(TokenType.AND):
            op = self._previous()
            right = self._equality()
            expr = LogicalExpr(location=op.location, left=expr, operator=op.type, right=right)
        return expr

    def _equality(self) -> Expression:
        expr = self._comparison()
        while self._match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            op = self._previous()
            right = self._comparison()
            expr = BinaryExpr(location=op.location, left=expr, operator=op.type, right=right)
        return expr

    def _comparison(self) -> Expression:
        expr = self._term()
        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            op = self._previous()
            right = self._term()
            expr = BinaryExpr(location=op.location, left=expr, operator=op.type, right=right)
        return expr

    def _term(self) -> Expression:
        expr = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous()
            right = self._factor()
            expr = BinaryExpr(location=op.location, left=expr, operator=op.type, right=right)
        return expr

    def _factor(self) -> Expression:
        expr = self._power()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self._previous()
            right = self._power()
            expr = BinaryExpr(location=op.location, left=expr, operator=op.type, right=right)
        return expr

    def _power(self) -> Expression:
        expr = self._unary()
        if self._match(TokenType.CARET):
            op = self._previous()
            # Exponentiation is right-associative: 2 ^ 3 ^ 2 == 2 ^ (3 ^ 2)
            right = self._power()
            return BinaryExpr(location=op.location, left=expr, operator=op.type, right=right)
        return expr

    def _unary(self) -> Expression:
        if self._match(TokenType.BANG, TokenType.NOT, TokenType.MINUS, TokenType.PLUS):
            op = self._previous()
            operand = self._unary()
            return UnaryExpr(location=op.location, operator=op.type, operand=operand)
        return self._call()

    def _call(self) -> Expression:
        expr = self._primary()

        while True:
            if self._match(TokenType.LPAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.LBRACKET):
                index_expr = self._expression()
                rbracket = self._consume(TokenType.RBRACKET, "Expected ']' after index")
                expr = IndexExpr(location=rbracket.location, target=expr, index=index_expr)
            else:
                break

        return expr

    def _finish_call(self, callee: Expression) -> Expression:
        args: List[Expression] = []
        loc = self._previous().location
        if not self._check(TokenType.RPAREN):
            args.append(self._expression())
            while self._match(TokenType.COMMA):
                args.append(self._expression())
        rparen = self._consume(TokenType.RPAREN, "Expected ')' after arguments")
        return CallExpr(location=loc, callee=callee, arguments=args)

    def _primary(self) -> Expression:
        tok = self._peek()

        if self._match(TokenType.TRUE):
            return LiteralExpr(location=tok.location, value=True)
        if self._match(TokenType.FALSE):
            return LiteralExpr(location=tok.location, value=False)
        if self._match(TokenType.NULL):
            return LiteralExpr(location=tok.location, value=None)
        if self._match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(location=tok.location, value=self._previous().value)

        if self._match(TokenType.IDENTIFIER):
            return IdentifierExpr(location=tok.location, name=self._previous().value)

        # Anonymous function: func(a, b) { ... }
        if self._match(TokenType.FUNC):
            loc = self._previous().location
            self._consume(TokenType.LPAREN, "Expected '(' after 'func'")
            params = self._parameters()
            self._consume(TokenType.RPAREN, "Expected ')' after parameters")
            self._consume(TokenType.LBRACE, "Expected '{' before function body")
            body = self._block_statement()
            return FunctionExpr(location=loc, params=params, body=body)

        # Parenthesized expression: ( expr )
        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr

        # List literal: [1, 2, 3]
        if self._match(TokenType.LBRACKET):
            loc = self._previous().location
            elements: List[Expression] = []
            if not self._check(TokenType.RBRACKET):
                elements.append(self._expression())
                while self._match(TokenType.COMMA):
                    if self._check(TokenType.RBRACKET):
                        break  # Allow trailing comma
                    elements.append(self._expression())
            self._consume(TokenType.RBRACKET, "Expected ']' after list elements")
            return ListExpr(location=loc, elements=elements)

        raise ParseError(
            f"Unexpected token {tok.type.name} ({tok.value!r}) in expression",
            line=tok.location.line,
            column=tok.location.column,
            source=self.source,
        )

    def _synchronize(self) -> None:
        """Skip tokens until the beginning of the next statement to recover from parse error."""
        self._advance()
        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return
            if self._peek().type in (
                TokenType.VAR,
                TokenType.CONST,
                TokenType.FUNC,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.FOR,
                TokenType.RETURN,
                TokenType.BREAK,
                TokenType.CONTINUE,
            ):
                return
            self._advance()
