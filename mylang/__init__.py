"""
MyLang - A modular, future-proof programming language written in pure Python.
"""

from typing import Any, Optional, TextIO
from mylang.ast import Program
from mylang.environment import Environment
from mylang.errors import MyLangError
from mylang.evaluator import Evaluator
from mylang.lexer import Lexer
from mylang.parser import Parser

__version__ = "0.1.0"


def execute(
    source: str,
    filename: str = "<stdin>",
    global_env: Optional[Environment] = None,
    output_stream: Optional[TextIO] = None,
) -> Any:
    """
    Executes a complete MyLang program from source code.
    Returns the value of the last evaluated expression/statement.
    """
    lexer = Lexer(source, filename=filename)
    tokens = lexer.tokenize()

    parser = Parser(tokens, source=source)
    ast: Program = parser.parse()

    evaluator = Evaluator(
        global_env=global_env,
        source=source,
        output_stream=output_stream,
    )
    return evaluator.evaluate(ast)
