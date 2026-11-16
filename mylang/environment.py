"""
Lexical environment and variable scoping for MyLang.
"""

from typing import Any, Dict, Optional, Set
from mylang.errors import RuntimeError
from mylang.tokens import SourceLocation


class Environment:
    """
    Tracks variable bindings in a hierarchical scope (lexical scoping).
    """

    def __init__(self, parent: Optional["Environment"] = None):
        self.parent = parent
        self.values: Dict[str, Any] = {}
        self.constants: Set[str] = set()

    def define(self, name: str, value: Any, is_const: bool = False) -> None:
        """Bind a variable in the current immediate scope."""
        self.values[name] = value
        if is_const:
            self.constants.add(name)
        elif name in self.constants:
            self.constants.remove(name)

    def get(self, name: str, loc: Optional[SourceLocation] = None, source: Optional[str] = None) -> Any:
        """Retrieve a variable from this scope or an enclosing parent scope."""
        if name in self.values:
            return self.values[name]

        if self.parent is not None:
            return self.parent.get(name, loc, source)

        line = loc.line if loc else None
        column = loc.column if loc else None
        raise RuntimeError(
            f"Undefined variable '{name}'",
            line=line,
            column=column,
            source=source,
        )

    def assign(self, name: str, value: Any, loc: Optional[SourceLocation] = None, source: Optional[str] = None) -> None:
        """Assign to an existing variable in this scope or an enclosing parent scope."""
        line = loc.line if loc else None
        column = loc.column if loc else None

        if name in self.values:
            if name in self.constants:
                raise RuntimeError(
                    f"Cannot reassign to constant '{name}'",
                    line=line,
                    column=column,
                    source=source,
                )
            self.values[name] = value
            return

        if self.parent is not None:
            self.parent.assign(name, value, loc, source)
            return

        raise RuntimeError(
            f"Cannot assign to undefined variable '{name}'",
            line=line,
            column=column,
            source=source,
        )

    def is_defined_here(self, name: str) -> bool:
        """Check if variable exists in this exact scope."""
        return name in self.values
