"""
Runtime representation of values and callables for MyLang.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, List, Optional
from mylang.errors import ReturnSignal, RuntimeError
from mylang.tokens import SourceLocation

if TYPE_CHECKING:
    from mylang.ast import BlockStmt
    from mylang.environment import Environment
    from mylang.evaluator import Evaluator


class MyLangCallable(ABC):
    """Abstract base class for all callable entities in MyLang."""

    @property
    @abstractmethod
    def arity(self) -> int:
        """Expected argument count. -1 indicates variadic arguments."""
        pass

    @abstractmethod
    def call(self, evaluator: "Evaluator", arguments: List[Any], loc: SourceLocation) -> Any:
        pass


class MyLangFunction(MyLangCallable):
    """User-defined function or closure."""

    def __init__(
        self,
        name: Optional[str],
        params: List[str],
        body: "BlockStmt",
        closure: "Environment",
    ):
        self.name = name or "<anonymous>"
        self.params = params
        self.body = body
        self.closure = closure

    @property
    def arity(self) -> int:
        return len(self.params)

    def call(self, evaluator: "Evaluator", arguments: List[Any], loc: SourceLocation) -> Any:
        from mylang.environment import Environment

        call_env = Environment(parent=self.closure)
        for param, arg in zip(self.params, arguments):
            call_env.define(param, arg)

        try:
            evaluator.execute_block(self.body.statements, call_env)
        except ReturnSignal as ret:
            return ret.value

        return None

    def __repr__(self) -> str:
        return f"<func {self.name}>"


class MyLangBuiltin(MyLangCallable):
    """Built-in standard library function."""

    def __init__(
        self,
        name: str,
        func: Callable[..., Any],
        expected_arity: int = -1,
    ):
        self.name = name
        self.func = func
        self._arity = expected_arity

    @property
    def arity(self) -> int:
        return self._arity

    def call(self, evaluator: "Evaluator", arguments: List[Any], loc: SourceLocation) -> Any:
        if self._arity != -1 and len(arguments) != self._arity:
            raise RuntimeError(
                f"Built-in '{self.name}' expected {self._arity} arguments, but got {len(arguments)}",
                line=loc.line,
                column=loc.column,
                source=evaluator.source,
            )
        try:
            return self.func(evaluator, arguments, loc)
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Error in '{self.name}': {exc}",
                line=loc.line,
                column=loc.column,
                source=evaluator.source,
            ) from exc

    def __repr__(self) -> str:
        return f"<builtin {self.name}>"


def is_truthy(val: Any) -> bool:
    """
    MyLang truthiness rule:
    'null' (None) and 'false' (False) are falsey.
    Everything else is truthy.
    """
    if val is None or val is False:
        return False
    return True


def stringify(val: Any) -> str:
    """Format any MyLang value into a clean human-readable string representation."""
    if val is None:
        return "null"
    if val is True:
        return "true"
    if val is False:
        return "false"
    if isinstance(val, float):
        # Format integer-equivalent floats nicely: 5.0 -> 5 if whole? No, keep float or standard repr
        text = str(val)
        if text.endswith(".0"):
            return text[:-2]
        return text
    if isinstance(val, list):
        items = [stringify(x) for x in val]
        return f"[{', '.join(items)}]"
    if isinstance(val, MyLangCallable):
        return repr(val)
    return str(val)
