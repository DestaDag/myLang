import unittest
from mylang.errors import LexerError
from mylang.lexer import Lexer
from mylang.tokens import TokenType


class TestLexer(unittest.TestCase):

    def test_numbers(self):
        source = "42 3.14 1e3 2.5e-2"
        tokens = Lexer(source).tokenize()
        types = [t.type for t in tokens]
        values = [t.value for t in tokens]

        self.assertEqual(types, [
            TokenType.NUMBER,
            TokenType.NUMBER,
            TokenType.NUMBER,
            TokenType.NUMBER,
            TokenType.EOF,
        ])
        self.assertEqual(values[0], 42)
        self.assertEqual(values[1], 3.14)
        self.assertEqual(values[2], 1000.0)
        self.assertAlmostEqual(values[3], 0.025)

    def test_strings_and_escapes(self):
        source = r'"hello world" "line\nbreak" "tab\tspace" "quote\"inner"'
        tokens = Lexer(source).tokenize()
        self.assertEqual(tokens[0].value, "hello world")
        self.assertEqual(tokens[1].value, "line\nbreak")
        self.assertEqual(tokens[2].value, "tab\tspace")
        self.assertEqual(tokens[3].value, 'quote"inner')

    def test_unterminated_string(self):
        with self.assertRaises(LexerError):
            Lexer('"unclosed string').tokenize()

    def test_identifiers_and_keywords(self):
        source = "var const func return if else while for to by break continue true false null and or not myVar_1"
        tokens = Lexer(source).tokenize()
        expected = [
            TokenType.VAR,
            TokenType.CONST,
            TokenType.FUNC,
            TokenType.RETURN,
            TokenType.IF,
            TokenType.ELSE,
            TokenType.WHILE,
            TokenType.FOR,
            TokenType.TO,
            TokenType.BY,
            TokenType.BREAK,
            TokenType.CONTINUE,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NULL,
            TokenType.AND,
            TokenType.OR,
            TokenType.NOT,
            TokenType.IDENTIFIER,
            TokenType.EOF,
        ]
        self.assertEqual([t.type for t in tokens], expected)
        self.assertEqual(tokens[-2].value, "myVar_1")

    def test_operators_and_delimiters(self):
        source = "+ - * / % ^ = += -= *= /= == != < <= > >= && || ( ) { } [ ] , ; : ."
        tokens = Lexer(source).tokenize()
        expected = [
            TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH, TokenType.PERCENT,
            TokenType.CARET, TokenType.EQUAL, TokenType.PLUS_EQUAL, TokenType.MINUS_EQUAL,
            TokenType.STAR_EQUAL, TokenType.SLASH_EQUAL, TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL,
            TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL,
            TokenType.AND, TokenType.OR,
            TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE, TokenType.RBRACE,
            TokenType.LBRACKET, TokenType.RBRACKET, TokenType.COMMA, TokenType.SEMICOLON,
            TokenType.COLON, TokenType.DOT,
            TokenType.EOF,
        ]
        self.assertEqual([t.type for t in tokens], expected)

    def test_comments(self):
        source = """
        // This is a single line comment
        var x = 10; /* multi-line
        comment */
        var y = 20;
        """
        tokens = Lexer(source).tokenize()
        # Should only get tokens for "var x = 10;" and "var y = 20;"
        values = [t.value for t in tokens if t.type != TokenType.EOF]
        self.assertEqual(values, ["var", "x", "=", 10, ";", "var", "y", "=", 20, ";"])

    def test_unterminated_multiline_comment(self):
        with self.assertRaises(LexerError):
            Lexer("/* unclosed comment").tokenize()


if __name__ == "__main__":
    unittest.main()
