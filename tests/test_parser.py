import unittest
from mylang.ast import (
    AssignExpr,
    BinaryExpr,
    CallExpr,
    ForStmt,
    FunctionStmt,
    IfStmt,
    IndexExpr,
    ListExpr,
    LiteralExpr,
    Program,
    ReturnStmt,
    VarStmt,
    WhileStmt,
)
from mylang.errors import ParseError
from mylang.lexer import Lexer
from mylang.parser import Parser
from mylang.tokens import TokenType


class TestParser(unittest.TestCase):

    def parse(self, code: str) -> Program:
        tokens = Lexer(code).tokenize()
        return Parser(tokens, source=code).parse()

    def test_precedence_arithmetic(self):
        # 2 + 3 * 4 should parse as 2 + (3 * 4)
        prog = self.parse("2 + 3 * 4;")
        expr_stmt = prog.statements[0]
        bin_expr = expr_stmt.expression
        self.assertIsInstance(bin_expr, BinaryExpr)
        self.assertEqual(bin_expr.operator, TokenType.PLUS)
        self.assertEqual(bin_expr.left.value, 2)
        self.assertIsInstance(bin_expr.right, BinaryExpr)
        self.assertEqual(bin_expr.right.operator, TokenType.STAR)

    def test_precedence_exponentiation(self):
        # Exponentiation is right-associative: 2 ^ 3 ^ 4 == 2 ^ (3 ^ 4)
        prog = self.parse("2 ^ 3 ^ 4;")
        bin_expr = prog.statements[0].expression
        self.assertEqual(bin_expr.operator, TokenType.CARET)
        self.assertEqual(bin_expr.left.value, 2)
        self.assertIsInstance(bin_expr.right, BinaryExpr)
        self.assertEqual(bin_expr.right.operator, TokenType.CARET)

    def test_let_and_const(self):
        prog = self.parse("var a = 1; const b = 2;")
        s1, s2 = prog.statements
        self.assertIsInstance(s1, VarStmt)
        self.assertEqual(s1.name, "a")
        self.assertFalse(s1.is_const)

        self.assertIsInstance(s2, VarStmt)
        self.assertEqual(s2.name, "b")
        self.assertTrue(s2.is_const)

    def test_const_without_initializer_raises(self):
        with self.assertRaises(ParseError):
            self.parse("const c;")

    def test_function_declaration(self):
        prog = self.parse("func add(x, y) { return x + y; }")
        fn_stmt = prog.statements[0]
        self.assertIsInstance(fn_stmt, FunctionStmt)
        self.assertEqual(fn_stmt.name, "add")
        self.assertEqual(fn_stmt.params, ["x", "y"])
        self.assertEqual(len(fn_stmt.body.statements), 1)
        self.assertIsInstance(fn_stmt.body.statements[0], ReturnStmt)

    def test_if_and_while(self):
        prog = self.parse("""
        if (x > 0) {
            y = 1;
        } else {
            y = -1;
        }
        while (y < 10) {
            y += 1;
        }
        """)
        self.assertIsInstance(prog.statements[0], IfStmt)
        self.assertIsInstance(prog.statements[1], WhileStmt)

    def test_list_and_index(self):
        prog = self.parse("var arr = [10, 20, 30]; arr[1] = 99;")
        var_stmt = prog.statements[0]
        self.assertIsInstance(var_stmt.initializer, ListExpr)
        self.assertEqual(len(var_stmt.initializer.elements), 3)

        assign_stmt = prog.statements[1].expression
        self.assertIsInstance(assign_stmt, AssignExpr)
        self.assertIsInstance(assign_stmt.target, IndexExpr)

    def test_for_loop(self):
        prog = self.parse("for i to 10 { x = i; }")
        for_stmt = prog.statements[0]
        self.assertIsInstance(for_stmt, ForStmt)
        self.assertEqual(for_stmt.var_name, "i")
        self.assertIsNone(for_stmt.start)
        self.assertEqual(for_stmt.end.value, 10)
        self.assertIsNone(for_stmt.step)

        prog2 = self.parse("for (i = 1 to 20 by 2) { x = i; }")
        for_stmt2 = prog2.statements[0]
        self.assertIsInstance(for_stmt2, ForStmt)
        self.assertEqual(for_stmt2.var_name, "i")
        self.assertEqual(for_stmt2.start.value, 1)
        self.assertEqual(for_stmt2.end.value, 20)
        self.assertEqual(for_stmt2.step.value, 2)


if __name__ == "__main__":
    unittest.main()
