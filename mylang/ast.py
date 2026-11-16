"""
Abstract Syntax Tree (AST) definitions and Visitor pattern for MyLang.
Designed for clean extensibility (compilers, type checkers, linters, optimizers).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional
from mylang.tokens import SourceLocation, TokenType


# --- Base Visitor Interface ---

class ASTVisitor(ABC):
    """
    Visitor interface for processing AST nodes.
    Subclasses can implement evaluators, code generators, type checkers, etc.
    """

    # Statements
    @abstractmethod
    def visit_program(self, node: "Program") -> Any:
        pass

    @abstractmethod
    def visit_block_stmt(self, node: "BlockStmt") -> Any:
        pass

    @abstractmethod
    def visit_expression_stmt(self, node: "ExpressionStmt") -> Any:
        pass

    @abstractmethod
    def visit_var_stmt(self, node: "VarStmt") -> Any:
        pass

    @abstractmethod
    def visit_function_stmt(self, node: "FunctionStmt") -> Any:
        pass

    @abstractmethod
    def visit_if_stmt(self, node: "IfStmt") -> Any:
        pass

    @abstractmethod
    def visit_while_stmt(self, node: "WhileStmt") -> Any:
        pass

    @abstractmethod
    def visit_for_stmt(self, node: "ForStmt") -> Any:
        pass

    @abstractmethod
    def visit_return_stmt(self, node: "ReturnStmt") -> Any:
        pass

    @abstractmethod
    def visit_break_stmt(self, node: "BreakStmt") -> Any:
        pass

    @abstractmethod
    def visit_continue_stmt(self, node: "ContinueStmt") -> Any:
        pass

    # Expressions
    @abstractmethod
    def visit_literal_expr(self, node: "LiteralExpr") -> Any:
        pass

    @abstractmethod
    def visit_identifier_expr(self, node: "IdentifierExpr") -> Any:
        pass

    @abstractmethod
    def visit_unary_expr(self, node: "UnaryExpr") -> Any:
        pass

    @abstractmethod
    def visit_binary_expr(self, node: "BinaryExpr") -> Any:
        pass

    @abstractmethod
    def visit_logical_expr(self, node: "LogicalExpr") -> Any:
        pass

    @abstractmethod
    def visit_assign_expr(self, node: "AssignExpr") -> Any:
        pass

    @abstractmethod
    def visit_call_expr(self, node: "CallExpr") -> Any:
        pass

    @abstractmethod
    def visit_function_expr(self, node: "FunctionExpr") -> Any:
        pass

    @abstractmethod
    def visit_list_expr(self, node: "ListExpr") -> Any:
        pass

    @abstractmethod
    def visit_index_expr(self, node: "IndexExpr") -> Any:
        pass


# --- AST Node Bases ---

@dataclass
class ASTNode(ABC):
    location: SourceLocation

    @abstractmethod
    def accept(self, visitor: ASTVisitor) -> Any:
        pass


@dataclass
class Statement(ASTNode):
    pass


@dataclass
class Expression(ASTNode):
    pass


# --- Statements ---

@dataclass
class Program(Statement):
    statements: List[Statement]

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_program(self)


@dataclass
class BlockStmt(Statement):
    statements: List[Statement]

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_block_stmt(self)


@dataclass
class ExpressionStmt(Statement):
    expression: Expression

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_expression_stmt(self)


@dataclass
class VarStmt(Statement):
    name: str
    initializer: Optional[Expression]
    is_const: bool = False

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_var_stmt(self)


@dataclass
class FunctionStmt(Statement):
    name: str
    params: List[str]
    body: BlockStmt

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_function_stmt(self)


@dataclass
class IfStmt(Statement):
    condition: Expression
    then_branch: Statement
    else_branch: Optional[Statement] = None

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_if_stmt(self)


@dataclass
class WhileStmt(Statement):
    condition: Expression
    body: Statement

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_while_stmt(self)


@dataclass
class ForStmt(Statement):
    var_name: str
    start: Optional[Expression]
    end: Expression
    step: Optional[Expression]
    body: Statement

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_for_stmt(self)


@dataclass
class ReturnStmt(Statement):
    value: Optional[Expression] = None

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_return_stmt(self)


@dataclass
class BreakStmt(Statement):
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_break_stmt(self)


@dataclass
class ContinueStmt(Statement):
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_continue_stmt(self)


# --- Expressions ---

@dataclass
class LiteralExpr(Expression):
    value: Any

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_literal_expr(self)


@dataclass
class IdentifierExpr(Expression):
    name: str

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_identifier_expr(self)


@dataclass
class UnaryExpr(Expression):
    operator: TokenType
    operand: Expression

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_unary_expr(self)


@dataclass
class BinaryExpr(Expression):
    left: Expression
    operator: TokenType
    right: Expression

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_binary_expr(self)


@dataclass
class LogicalExpr(Expression):
    left: Expression
    operator: TokenType
    right: Expression

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_logical_expr(self)


@dataclass
class AssignExpr(Expression):
    target: Expression  # IdentifierExpr or IndexExpr
    value: Expression

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_assign_expr(self)


@dataclass
class CallExpr(Expression):
    callee: Expression
    arguments: List[Expression]

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_call_expr(self)


@dataclass
class FunctionExpr(Expression):
    params: List[str]
    body: BlockStmt

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_function_expr(self)


@dataclass
class ListExpr(Expression):
    elements: List[Expression]

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_list_expr(self)


@dataclass
class IndexExpr(Expression):
    target: Expression
    index: Expression

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_index_expr(self)
