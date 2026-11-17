"""
Evaluator (Tree-walk interpreter) for MyLang AST.
Implements the ASTVisitor interface for clean separation of syntax and execution.
"""

import math
import sys
import time
from typing import Any, List, Optional, TextIO
from mylang.ast import (
    ASTNode,
    ASTVisitor,
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
from mylang.environment import Environment
from mylang.errors import BreakSignal, ContinueSignal, ReturnSignal, RuntimeError
from mylang.tokens import SourceLocation, TokenType
from mylang.values import MyLangBuiltin, MyLangCallable, MyLangFunction, is_truthy, stringify


class Evaluator(ASTVisitor):
    """
    Tree-walking interpreter that executes the MyLang AST.
    """

    def __init__(
        self,
        global_env: Optional[Environment] = None,
        source: Optional[str] = None,
        output_stream: Optional[TextIO] = None,
    ):
        self.source = source
        self.output_stream: TextIO = output_stream if output_stream is not None else sys.stdout

        if global_env is not None:
            self.globals = global_env
        else:
            self.globals = Environment()
            self._register_builtins(self.globals)

        self.environment = self.globals

    def _register_builtins(self, env: Environment) -> None:
        """Register the built-in standard library functions."""

        def b_print(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> Any:
            text = " ".join(stringify(a) for a in args)
            evaluator.output_stream.write(text + "\n")
            evaluator.output_stream.flush()
            return None

        def b_len(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> Any:
            val = args[0]
            if isinstance(val, (list, str)):
                return len(val)
            raise RuntimeError(
                f"Cannot compute len() of type '{type(val).__name__}'",
                line=loc.line,
                column=loc.column,
                source=evaluator.source,
            )

        def b_type(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> str:
            val = args[0]
            if val is None:
                return "null"
            if isinstance(val, bool):
                return "boolean"
            if isinstance(val, (int, float)):
                return "number"
            if isinstance(val, str):
                return "string"
            if isinstance(val, list):
                return "list"
            if isinstance(val, MyLangCallable):
                return "function"
            return type(val).__name__

        def b_range(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> List[int]:
            if len(args) == 1:
                return list(range(int(args[0])))
            elif len(args) == 2:
                return list(range(int(args[0]), int(args[1])))
            elif len(args) == 3:
                return list(range(int(args[0]), int(args[1]), int(args[2])))
            raise RuntimeError(
                f"range() expects 1 to 3 arguments, got {len(args)}",
                line=loc.line,
                column=loc.column,
                source=evaluator.source,
            )

        def b_push(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> List[Any]:
            target, item = args[0], args[1]
            if not isinstance(target, list):
                raise RuntimeError(
                    f"push() expects a list as first argument, got {type(target).__name__}",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            target.append(item)
            return target

        def b_pop(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> Any:
            target = args[0]
            if not isinstance(target, list):
                raise RuntimeError(
                    f"pop() expects a list as first argument, got {type(target).__name__}",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            if not target:
                raise RuntimeError(
                    "pop() on an empty list",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            return target.pop()

        def b_clock(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> float:
            return time.time()

        def b_str(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> str:
            return stringify(args[0])

        def b_int(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> int:
            try:
                return int(args[0])
            except (ValueError, TypeError) as exc:
                raise RuntimeError(
                    f"Cannot convert {args[0]!r} to int",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                ) from exc

        def b_float(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> float:
            try:
                return float(args[0])
            except (ValueError, TypeError) as exc:
                raise RuntimeError(
                    f"Cannot convert {args[0]!r} to float",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                ) from exc

        def b_assert(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> None:
            cond = args[0]
            msg = args[1] if len(args) > 1 else "Assertion failed"
            if not is_truthy(cond):
                raise RuntimeError(
                    f"AssertionError: {msg}",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            return None

        def b_slice(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> Any:
            if len(args) < 2 or len(args) > 3:
                raise RuntimeError(
                    f"slice() expects 2 or 3 arguments, got {len(args)}",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            seq, start = args[0], args[1]
            if not isinstance(seq, (list, str)):
                raise RuntimeError(
                    f"slice() expects a list or string as first argument, got '{type(seq).__name__}'",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            if not isinstance(start, int):
                raise RuntimeError(
                    f"slice() start index must be an integer, got '{type(start).__name__}'",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            end = None
            if len(args) == 3 and args[2] is not None:
                end = args[2]
                if not isinstance(end, int):
                    raise RuntimeError(
                        f"slice() end index must be an integer, got '{type(end).__name__}'",
                        line=loc.line,
                        column=loc.column,
                        source=evaluator.source,
                    )

            if isinstance(seq, list):
                return seq[start:end] if end is not None else seq[start:]
            else:
                return seq[start:end] if end is not None else seq[start:]

        def b_split(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> List[str]:
            if len(args) < 1 or len(args) > 2:
                raise RuntimeError(
                    f"split() expects 1 or 2 arguments, got {len(args)}",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            target = args[0]
            if not isinstance(target, str):
                raise RuntimeError(
                    f"split() expects a string as first argument, got '{type(target).__name__}'",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            sep = args[1] if len(args) == 2 else None
            if sep is not None and not isinstance(sep, str):
                raise RuntimeError(
                    f"split() separator must be a string, got '{type(sep).__name__}'",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            return target.split(sep)

        def b_join(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> str:
            if len(args) < 1 or len(args) > 2:
                raise RuntimeError(
                    f"join() expects 1 or 2 arguments, got {len(args)}",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            target_list = args[0]
            if not isinstance(target_list, list):
                raise RuntimeError(
                    f"join() expects a list as first argument, got '{type(target_list).__name__}'",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            sep = args[1] if len(args) == 2 else ""
            if not isinstance(sep, str):
                raise RuntimeError(
                    f"join() separator must be a string, got '{type(sep).__name__}'",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            return sep.join(stringify(item) for item in target_list)

        def b_abs(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> Any:
            val = args[0]
            if not isinstance(val, (int, float)):
                raise RuntimeError(
                    f"abs() expects a number, got '{type(val).__name__}'",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            return abs(val)

        def b_sign(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> int:
            val = args[0]
            if not isinstance(val, (int, float)):
                raise RuntimeError(
                    f"sign() expects a number, got '{type(val).__name__}'",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            if val > 0:
                return 1
            elif val < 0:
                return -1
            return 0

        def b_min(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> Any:
            if len(args) == 0:
                raise RuntimeError(
                    "min() expects at least 1 argument, got 0",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            if len(args) == 1 and isinstance(args[0], list):
                items = args[0]
                if len(items) == 0:
                    raise RuntimeError(
                        "min() on an empty list",
                        line=loc.line,
                        column=loc.column,
                        source=evaluator.source,
                    )
            else:
                items = args

            try:
                return min(items)
            except TypeError as exc:
                raise RuntimeError(
                    f"min() comparison error: {exc}",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                ) from exc

        def b_max(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> Any:
            if len(args) == 0:
                raise RuntimeError(
                    "max() expects at least 1 argument, got 0",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            if len(args) == 1 and isinstance(args[0], list):
                items = args[0]
                if len(items) == 0:
                    raise RuntimeError(
                        "max() on an empty list",
                        line=loc.line,
                        column=loc.column,
                        source=evaluator.source,
                    )
            else:
                items = args

            try:
                return max(items)
            except TypeError as exc:
                raise RuntimeError(
                    f"max() comparison error: {exc}",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                ) from exc

        def b_clamp(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> Any:
            val, min_val, max_val = args[0], args[1], args[2]
            for name, v in [("val", val), ("min_val", min_val), ("max_val", max_val)]:
                if not isinstance(v, (int, float)):
                    raise RuntimeError(
                        f"clamp() {name} must be a number, got '{type(v).__name__}'",
                        line=loc.line,
                        column=loc.column,
                        source=evaluator.source,
                    )
            if min_val > max_val:
                raise RuntimeError(
                    f"clamp() min_val ({min_val}) cannot be greater than max_val ({max_val})",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            return min(max(val, min_val), max_val)

        def b_rem(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> Any:
            x, y = args[0], args[1]
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                raise RuntimeError(
                    f"rem() arguments must be numbers, got '{type(x).__name__}' and '{type(y).__name__}'",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            if y == 0:
                raise RuntimeError(
                    "rem() division by zero",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            return x % y

        def b_gcd(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> int:
            a, b = args[0], args[1]
            if not isinstance(a, int) or not isinstance(b, int):
                raise RuntimeError(
                    f"gcd() arguments must be integers, got '{type(a).__name__}' and '{type(b).__name__}'",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            return math.gcd(a, b)

        def b_lcm(evaluator: "Evaluator", args: List[Any], loc: SourceLocation) -> int:
            a, b = args[0], args[1]
            if not isinstance(a, int) or not isinstance(b, int):
                raise RuntimeError(
                    f"lcm() arguments must be integers, got '{type(a).__name__}' and '{type(b).__name__}'",
                    line=loc.line,
                    column=loc.column,
                    source=evaluator.source,
                )
            return math.lcm(a, b)

        env.define("print", MyLangBuiltin("print", b_print, expected_arity=-1))
        env.define("println", MyLangBuiltin("println", b_print, expected_arity=-1))
        env.define("len", MyLangBuiltin("len", b_len, expected_arity=1))
        env.define("type", MyLangBuiltin("type", b_type, expected_arity=1))
        env.define("range", MyLangBuiltin("range", b_range, expected_arity=-1))
        env.define("push", MyLangBuiltin("push", b_push, expected_arity=2))
        env.define("pop", MyLangBuiltin("pop", b_pop, expected_arity=1))
        env.define("clock", MyLangBuiltin("clock", b_clock, expected_arity=0))
        env.define("str", MyLangBuiltin("str", b_str, expected_arity=1))
        env.define("int", MyLangBuiltin("int", b_int, expected_arity=1))
        env.define("float", MyLangBuiltin("float", b_float, expected_arity=1))
        env.define("assert", MyLangBuiltin("assert", b_assert, expected_arity=-1))
        env.define("slice", MyLangBuiltin("slice", b_slice, expected_arity=-1))
        env.define("split", MyLangBuiltin("split", b_split, expected_arity=-1))
        env.define("join", MyLangBuiltin("join", b_join, expected_arity=-1))
        env.define("abs", MyLangBuiltin("abs", b_abs, expected_arity=1))
        env.define("sign", MyLangBuiltin("sign", b_sign, expected_arity=1))
        env.define("min", MyLangBuiltin("min", b_min, expected_arity=-1))
        env.define("max", MyLangBuiltin("max", b_max, expected_arity=-1))
        env.define("clamp", MyLangBuiltin("clamp", b_clamp, expected_arity=3))
        env.define("rem", MyLangBuiltin("rem", b_rem, expected_arity=2))
        env.define("gcd", MyLangBuiltin("gcd", b_gcd, expected_arity=2))
        env.define("lcm", MyLangBuiltin("lcm", b_lcm, expected_arity=2))

    # --- Top-Level Evaluation ---

    def evaluate(self, node: ASTNode) -> Any:
        return node.accept(self)

    def execute_block(self, statements: List[Statement], environment: Environment) -> Any:
        previous_env = self.environment
        last_val = None
        try:
            self.environment = environment
            for stmt in statements:
                last_val = self.evaluate(stmt)
            return last_val
        finally:
            self.environment = previous_env

    # --- Statements ---

    def visit_program(self, node: Program) -> Any:
        last_value = None
        for stmt in node.statements:
            last_value = self.evaluate(stmt)
        return last_value

    def visit_block_stmt(self, node: BlockStmt) -> Any:
        return self.execute_block(node.statements, Environment(parent=self.environment))

    def visit_expression_stmt(self, node: ExpressionStmt) -> Any:
        return self.evaluate(node.expression)

    def visit_var_stmt(self, node: VarStmt) -> Any:
        value = None
        if node.initializer is not None:
            value = self.evaluate(node.initializer)
        self.environment.define(node.name, value, is_const=node.is_const)
        return value

    def visit_function_stmt(self, node: FunctionStmt) -> Any:
        function = MyLangFunction(
            name=node.name,
            params=node.params,
            body=node.body,
            closure=self.environment,
        )
        self.environment.define(node.name, function)
        return function

    def visit_if_stmt(self, node: IfStmt) -> Any:
        cond_val = self.evaluate(node.condition)
        if is_truthy(cond_val):
            return self.evaluate(node.then_branch)
        elif node.else_branch is not None:
            return self.evaluate(node.else_branch)
        return None

    def visit_while_stmt(self, node: WhileStmt) -> Any:
        last_val = None
        while is_truthy(self.evaluate(node.condition)):
            try:
                last_val = self.evaluate(node.body)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
        return last_val

    def visit_for_stmt(self, node: ForStmt) -> Any:
        # 1. Determine start value
        if node.start is not None:
            current_val = self.evaluate(node.start)
        else:
            try:
                current_val = self.environment.get(node.var_name, node.location, self.source)
            except RuntimeError:
                current_val = 0

        # 2. Evaluate end target
        end_val = self.evaluate(node.end)

        # 3. Determine step value
        if node.step is not None:
            step_val = self.evaluate(node.step)
        else:
            step_val = 1

        # Type validation
        if not isinstance(current_val, (int, float)):
            raise RuntimeError(
                f"For loop initial value must be a number, got '{type(current_val).__name__}'",
                line=node.location.line,
                column=node.location.column,
                source=self.source,
            )
        if not isinstance(end_val, (int, float)):
            raise RuntimeError(
                f"For loop 'to' target must be a number, got '{type(end_val).__name__}'",
                line=node.location.line,
                column=node.location.column,
                source=self.source,
            )
        if not isinstance(step_val, (int, float)):
            raise RuntimeError(
                f"For loop 'by' step must be a number, got '{type(step_val).__name__}'",
                line=node.location.line,
                column=node.location.column,
                source=self.source,
            )
        if step_val == 0:
            raise RuntimeError(
                "For loop 'by' step cannot be zero",
                line=node.location.line,
                column=node.location.column,
                source=self.source,
            )

        loop_env = Environment(parent=self.environment)
        previous_env = self.environment
        last_val = None

        try:
            self.environment = loop_env
            loop_env.define(node.var_name, current_val)

            while True:
                # Condition check based on step direction:
                # Positive step: loop while current_val <= end_val
                # Negative step: loop while current_val >= end_val
                if step_val > 0:
                    if current_val > end_val:
                        break
                else:
                    if current_val < end_val:
                        break

                loop_env.assign(node.var_name, current_val)
                if previous_env.is_defined_here(node.var_name):
                    previous_env.assign(node.var_name, current_val)

                try:
                    last_val = self.evaluate(node.body)
                except BreakSignal:
                    break
                except ContinueSignal:
                    pass

                # Read current variable value (in case mutated inside loop body) and apply step
                updated_val = loop_env.get(node.var_name)
                current_val = updated_val + step_val
                loop_env.assign(node.var_name, current_val)
                if previous_env.is_defined_here(node.var_name):
                    previous_env.assign(node.var_name, current_val)

            return last_val
        finally:
            self.environment = previous_env

    def visit_return_stmt(self, node: ReturnStmt) -> Any:
        value = None
        if node.value is not None:
            value = self.evaluate(node.value)
        raise ReturnSignal(value)

    def visit_break_stmt(self, node: BreakStmt) -> Any:
        raise BreakSignal()

    def visit_continue_stmt(self, node: ContinueStmt) -> Any:
        raise ContinueSignal()

    # --- Expressions ---

    def visit_literal_expr(self, node: LiteralExpr) -> Any:
        return node.value

    def visit_identifier_expr(self, node: IdentifierExpr) -> Any:
        return self.environment.get(node.name, node.location, self.source)

    def visit_unary_expr(self, node: UnaryExpr) -> Any:
        operand = self.evaluate(node.operand)

        if node.operator in (TokenType.BANG, TokenType.NOT):
            return not is_truthy(operand)
        if node.operator == TokenType.MINUS:
            if not isinstance(operand, (int, float)):
                raise RuntimeError(
                    f"Unary '-' operand must be a number, got {type(operand).__name__}",
                    line=node.location.line,
                    column=node.location.column,
                    source=self.source,
                )
            return -operand
        if node.operator == TokenType.PLUS:
            if not isinstance(operand, (int, float)):
                raise RuntimeError(
                    f"Unary '+' operand must be a number, got {type(operand).__name__}",
                    line=node.location.line,
                    column=node.location.column,
                    source=self.source,
                )
            return +operand

        raise RuntimeError(
            f"Unknown unary operator {node.operator.name}",
            line=node.location.line,
            column=node.location.column,
            source=self.source,
        )

    def visit_binary_expr(self, node: BinaryExpr) -> Any:
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        op = node.operator

        # Addition / Concatenation
        if op == TokenType.PLUS:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            if isinstance(left, str) or isinstance(right, str):
                return stringify(left) + stringify(right)
            if isinstance(left, list) and isinstance(right, list):
                return left + right
            raise RuntimeError(
                f"Unsupported operand types for '+': '{type(left).__name__}' and '{type(right).__name__}'",
                line=node.location.line,
                column=node.location.column,
                source=self.source,
            )

        # Arithmetic operations
        if op in (TokenType.MINUS, TokenType.STAR, TokenType.SLASH, TokenType.PERCENT, TokenType.CARET):
            if not (isinstance(left, (int, float)) and isinstance(right, (int, float))):
                raise RuntimeError(
                    f"Operands for {op.name} must be numbers, got '{type(left).__name__}' and '{type(right).__name__}'",
                    line=node.location.line,
                    column=node.location.column,
                    source=self.source,
                )
            if op == TokenType.MINUS:
                return left - right
            if op == TokenType.STAR:
                return left * right
            if op == TokenType.SLASH:
                if right == 0:
                    raise RuntimeError(
                        "Division by zero",
                        line=node.location.line,
                        column=node.location.column,
                        source=self.source,
                    )
                # Keep int division clean if exact, otherwise float
                res = left / right
                return int(res) if res.is_integer() else res
            if op == TokenType.PERCENT:
                if right == 0:
                    raise RuntimeError(
                        "Modulo by zero",
                        line=node.location.line,
                        column=node.location.column,
                        source=self.source,
                    )
                return left % right
            if op == TokenType.CARET:
                res = left ** right
                if isinstance(res, complex):
                    raise RuntimeError(
                        "Complex number results are not supported",
                        line=node.location.line,
                        column=node.location.column,
                        source=self.source,
                    )
                if isinstance(res, float) and res.is_integer():
                    return int(res)
                return res

        # Comparisons
        if op in (TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            if type(left) != type(right) and not (isinstance(left, (int, float)) and isinstance(right, (int, float))):
                raise RuntimeError(
                    f"Cannot compare different types: '{type(left).__name__}' and '{type(right).__name__}'",
                    line=node.location.line,
                    column=node.location.column,
                    source=self.source,
                )
            if op == TokenType.GREATER:
                return left > right
            if op == TokenType.GREATER_EQUAL:
                return left >= right
            if op == TokenType.LESS:
                return left < right
            if op == TokenType.LESS_EQUAL:
                return left <= right

        # Equality
        if op == TokenType.EQUAL_EQUAL:
            return left == right
        if op == TokenType.BANG_EQUAL:
            return left != right

        raise RuntimeError(
            f"Unknown binary operator {op.name}",
            line=node.location.line,
            column=node.location.column,
            source=self.source,
        )

    def visit_logical_expr(self, node: LogicalExpr) -> Any:
        left = self.evaluate(node.left)

        if node.operator == TokenType.OR:
            if is_truthy(left):
                return left
            return self.evaluate(node.right)
        elif node.operator == TokenType.AND:
            if not is_truthy(left):
                return left
            return self.evaluate(node.right)

        raise RuntimeError(
            f"Unknown logical operator {node.operator.name}",
            line=node.location.line,
            column=node.location.column,
            source=self.source,
        )

    def visit_assign_expr(self, node: AssignExpr) -> Any:
        value = self.evaluate(node.value)

        if isinstance(node.target, IdentifierExpr):
            self.environment.assign(node.target.name, value, node.location, self.source)
            return value

        if isinstance(node.target, IndexExpr):
            collection = self.evaluate(node.target.target)
            idx = self.evaluate(node.target.index)

            if not isinstance(collection, list):
                raise RuntimeError(
                    f"Only lists support index assignment, got '{type(collection).__name__}'",
                    line=node.location.line,
                    column=node.location.column,
                    source=self.source,
                )
            if not isinstance(idx, int):
                raise RuntimeError(
                    f"List index must be an integer, got '{type(idx).__name__}'",
                    line=node.location.line,
                    column=node.location.column,
                    source=self.source,
                )
            if idx < -len(collection) or idx >= len(collection):
                raise RuntimeError(
                    f"List index {idx} out of range (length {len(collection)})",
                    line=node.location.line,
                    column=node.location.column,
                    source=self.source,
                )
            collection[idx] = value
            return value

        raise RuntimeError(
            f"Invalid assignment target {node.target}",
            line=node.location.line,
            column=node.location.column,
            source=self.source,
        )

    def visit_call_expr(self, node: CallExpr) -> Any:
        callee = self.evaluate(node.callee)
        arguments = [self.evaluate(arg) for arg in node.arguments]

        if not isinstance(callee, MyLangCallable):
            raise RuntimeError(
                f"Can only call functions, got '{type(callee).__name__}'",
                line=node.location.line,
                column=node.location.column,
                source=self.source,
            )

        if callee.arity != -1 and len(arguments) != callee.arity:
            raise RuntimeError(
                f"Expected {callee.arity} arguments but got {len(arguments)}",
                line=node.location.line,
                column=node.location.column,
                source=self.source,
            )

        return callee.call(self, arguments, node.location)

    def visit_function_expr(self, node: FunctionExpr) -> Any:
        return MyLangFunction(
            name=None,
            params=node.params,
            body=node.body,
            closure=self.environment,
        )

    def visit_list_expr(self, node: ListExpr) -> Any:
        return [self.evaluate(elem) for elem in node.elements]

    def visit_index_expr(self, node: IndexExpr) -> Any:
        target = self.evaluate(node.target)
        index = self.evaluate(node.index)

        if not isinstance(index, int):
            raise RuntimeError(
                f"Index must be an integer, got '{type(index).__name__}'",
                line=node.location.line,
                column=node.location.column,
                source=self.source,
            )

        if isinstance(target, (list, str)):
            if index < -len(target) or index >= len(target):
                raise RuntimeError(
                    f"Index {index} out of range (length {len(target)})",
                    line=node.location.line,
                    column=node.location.column,
                    source=self.source,
                )
            return target[index]

        raise RuntimeError(
            f"Type '{type(target).__name__}' is not indexable",
            line=node.location.line,
            column=node.location.column,
            source=self.source,
        )
