# MyLang

A modular, expressive, and future-proof programming language written in **100% pure Python** (no third-party dependencies required).

MyLang implements an end-to-end interpreter pipeline consisting of a **Lexer**, **Recursive-Descent Parser**, **Abstract Syntax Tree (AST) with the Visitor Pattern**, and a **Tree-Walking Evaluator** with lexical scoping, first-class functions, and closures.

---

## Table of Contents

- [Architecture & Design](#architecture--design)
- [Project Layout](#project-layout)
- [Language Features](#language-features)
  - [Variables & Constants](#variables--constants)
  - [Data Types](#data-types)
  - [Operators & Precedence](#operators--precedence)
  - [Control Flow](#control-flow)
  - [Functions & Closures](#functions--closures)
  - [Lists & Collections](#lists--collections)
  - [Built-in Functions](#built-in-functions)
- [Getting Started](#getting-started)
  - [Interactive REPL](#interactive-repl)
  - [Running Source Files](#running-source-files)
  - [Running Tests](#running-tests)
- [Future-Proofing & Extensibility Guide](#future-proofing--extensibility-guide)
  - [1. Adding a New Token](#1-adding-a-new-token)
  - [2. Adding a New AST Node & Syntax Rule](#2-adding-a-new-ast-node--syntax-rule)
  - [3. Implementing New AST Passes (Type Checker, Bytecode VM)](#3-implementing-new-ast-passes-type-checker-bytecode-vm)
  - [4. Adding Standard Library Built-ins](#4-adding-standard-library-built-ins)
- [Roadmap](#roadmap)

---

## Architecture & Design

The language is engineered with strict separation of concerns to make future evolutions (such as adding a bytecode compiler, static analyzer, or optimizer) clean and straightforward.

```
Source Code (.ml)
       │
       ▼
 [ Lexer / Tokenizer ]  ──> Tokens with line & column locations
       │
       ▼
 [  Parser (RD/Pratt) ] ──> Strongly-typed AST nodes
       │
       ▼
 [ ASTVisitor Engine ]  ──> Evaluator / TypeChecker / Compiler
       │
       ▼
 [  Runtime & Scope  ]  ──> Lexical Environments & Values
```

- **Lexer (`mylang/lexer.py`)**: Converts character streams into structured tokens while tracking precise line and column numbers. Handles multi-line comments, string escape sequences, and scientific float notation.
- **AST (`mylang/ast.py`)**: Strongly-typed node definitions based on Python dataclasses. Implements the classic **Visitor Pattern** (`ASTVisitor`), completely separating grammar nodes from transformation and evaluation logic.
- **Parser (`mylang/parser.py`)**: Recursive descent parser with precedence climbing. Produces informative syntax errors with contextual source code snippets and pointer carets.
- **Environment (`mylang/environment.py`)**: Implements lexical scoping with parent-link delegation, enabling variable shadowing, global variables, and true closures.
- **Evaluator (`mylang/evaluator.py`)**: Implements `ASTVisitor` to execute AST nodes. Handles control flow (`return`, `break`, `continue`), truthiness rules, error handling, and standard library built-ins.

---

## Project Layout

```
myLang/
├── main.py                     # CLI entry point (REPL & file runner)
├── README.md                   # Complete language documentation
├── mylang/
│   ├── __init__.py             # Public API (`execute()`, `__version__`)
│   ├── __main__.py             # Enables `python -m mylang`
│   ├── tokens.py               # TokenType enum, SourceLocation, and Token
│   ├── lexer.py                # Tokenizer with source location tracking
│   ├── ast.py                  # AST nodes and ASTVisitor interface
│   ├── parser.py               # Recursive descent parser
│   ├── environment.py          # Lexical environments and scope chains
│   ├── values.py               # Runtime values, callables, stringifier
│   ├── evaluator.py            # AST visitor tree-walk interpreter & builtins
│   ├── errors.py               # Formatted error reporting with carets
│   └── repl.py                 # Multi-line interactive REPL
├── examples/
│   ├── 01_basics.ml            # Variables, constants, arithmetic
│   ├── 02_control_flow.ml      # If/else, while, for loops, break/continue
│   ├── 03_functions_and_closures.ml # First-class functions, recursion, closures
│   ├── 04_lists.ml             # Lists, indexing, push/pop, range
│   └── 05_fibonacci.ml         # Benchmark calculation with timer
└── tests/
    ├── __init__.py
    ├── test_lexer.py           # Lexer unit tests
    ├── test_parser.py          # Parser & precedence unit tests
    └── test_evaluator.py       # Runtime execution & error tests
```

---

## Language Features

### Variables & Constants

```javascript
var count = 10;          // Mutable variable
count = count + 1;       // Reassignment
count += 5;              // Compound assignment (+=, -=, *=, /=)

const MAX_USERS = 100;   // Immutable constant
// MAX_USERS = 200;      // Error: Cannot reassign to constant 'MAX_USERS'
```

### Data Types

- **Numbers**: Integers (`42`, `-7`) and floating-point (`3.14`, `1e5`).
- **Strings**: Single or double-quoted (`"Hello\nWorld"`, `'hello'`) supporting escape characters.
- **Booleans**: `true` and `false`.
- **Null**: `null` (or `nil`).
- **Lists**: Ordered mutable collections (`[1, 2, "three", true]`).
- **Functions**: First-class callables (`func(x) { return x * 2; }`).

### Operators & Precedence

Precedence (highest to lowest):
1. Primary / Grouping: `()`, `[]`, literals, identifiers
2. Function call & Indexing: `foo()`, `arr[0]`
3. Unary: `-`, `+`, `!`, `not`
4. Exponentiation: `^` (right-associative: `2 ^ 3 ^ 2 == 512`)
5. Multiplication / Division / Modulo: `*`, `/`, `%`
6. Addition / Subtraction / String Concat: `+`, `-`
7. Comparisons: `<`, `<=`, `>`, `>=`
8. Equality: `==`, `!=`
9. Logical AND: `and`, `&&` (short-circuiting)
10. Logical OR: `or`, `||` (short-circuiting)
11. Assignment: `=`, `+=`, `-=`, `*=`, `/=`

### Control Flow

#### If-Else Statements
```javascript
var score = 85;

if (score >= 90) {
    println("Grade: A");
} else if (score >= 80) {
    println("Grade: B");
} else {
    println("Grade: C or below");
}
```

#### While Loops
```javascript
var x = 3;
while (x > 0) {
    println("Countdown:", x);
    x -= 1;
}
```

#### For Loops
Iterate using `for <var> to <n>` (default step of `+1`) or `for <var> to <n> by <x>` (where `x` is a positive or negative integer step). Supports `break` and `continue`:

```javascript
// Default +1 increment from 0 to 5:
for i to 5 {
    println(i); // 0, 1, 2, 3, 4, 5
}

// Starting from an initial value with positive step:
for i = 1 to 10 by 2 {
    println(i); // 1, 3, 5, 7, 9
}

// Countdown using negative step:
for i = 10 to 1 by -1 {
    println(i); // 10, 9, 8, ..., 1
}

// With break and continue:
for i = 1 to 10 {
    if (i % 2 == 0) {
        continue; // Skip even numbers
    }
    if (i > 7) {
        break; // Stop when i > 7
    }
    println("Odd number:", i);
}
```

### Functions & Closures

Functions are first-class citizens. They can be named, stored in variables, passed to other functions, and returned from functions while retaining their lexical scope:

```javascript
// Named declaration
func add(a, b) {
    return a + b;
}

// Anonymous function / Lambda expression
var multiply = func(x, y) {
    return x * y;
};

// Higher-order function
func apply(f, val) {
    return f(val);
}

// Lexical closure
func makeMultiplier(factor) {
    return func(val) {
        return val * factor;
    };
}

var triple = makeMultiplier(3);
println(triple(10)); // Outputs: 30
```

### Lists & Collections

```javascript
var items = [10, 20, 30];

println(items[0]);       // 10
println(items[-1]);      // 30 (supports negative indices)

items[1] = 999;          // List item mutation
push(items, 40);         // Append element
var last = pop(items);   // Remove and return last element
println("Length:", len(items));
```

### Built-in Functions

| Function | Signature | Description |
|---|---|---|
| `print(...)` | `(...args)` | Prints arguments space-separated with newline |
| `println(...)` | `(...args)` | Alias for `print` |
| `len(x)` | `(str \| list)` | Returns the length of a string or list |
| `type(x)` | `(val)` | Returns type name ("number", "string", "list", etc.) |
| `range(start, end, step?)` | `(start, [end, [step]])` | Generates a list of numbers |
| `push(list, val)` | `(list, val)` | Appends `val` to `list` and returns the list |
| `pop(list)` | `(list)` | Pops and returns the last element of `list` |
| `clock()` | `()` | Returns current epoch time in seconds |
| `str(val)` | `(val)` | Converts value to string representation |
| `int(val)` | `(val)` | Converts string or float to integer |
| `float(val)` | `(val)` | Converts string or integer to float |
| `assert(cond, msg?)` | `(cond, [msg])` | Raises an error if condition is falsey |
| `slice(seq, start, end?)` | `(str \| list, int, [int])` | Extracts a sub-sequence without mutating the original |
| `split(str, sep?)` | `(str, [str])` | Splits a string into a list of substrings |
| `join(list, sep)` | `(list, str)` | Concatenates list elements into a single string |

---

## Getting Started

### Interactive REPL

Start the REPL by running:
```bash
python3 main.py
# or
python3 -m mylang
```

**REPL Commands:**
- `:help` - Display available commands
- `:env` - Inspect global variables and constants
- `:tokens <code>` - Print token stream produced by the lexer
- `:ast <code>` - Inspect the parsed Abstract Syntax Tree
- `:exit` / `:q` - Exit the shell

Multi-line blocks (e.g. unclosed `{`, `(`, `[`) automatically trigger the continuation prompt `... ` until closed.

### Running Source Files

Execute any `.ml` source script:
```bash
python3 main.py examples/01_basics.ml
python3 main.py examples/03_functions_and_closures.ml
python3 main.py examples/05_fibonacci.ml
```

### Running Tests

The test suite is built on Python's native `unittest` module:
```bash
python3 -m unittest discover tests
```

---

## Future-Proofing & Extensibility Guide

MyLang is structured so that adding features or replacing the execution backend does not require rewriting other layers.

### 1. Adding a New Token

1. Add the enum variant in `mylang/tokens.py`:
   ```python
   class TokenType(Enum):
       # ...
       MATCH = auto()
   ```
2. If it's a keyword, register it in `KEYWORDS` in `mylang/tokens.py`:
   ```python
   KEYWORDS["match"] = TokenType.MATCH
   ```
3. If it's a symbol (e.g. `->`), add the matching logic in `Lexer._next_token()` in `mylang/lexer.py`.

### 2. Adding a New AST Node & Syntax Rule

1. Define the node dataclass in `mylang/ast.py`:
   ```python
   @dataclass
   class AssertStmt(Statement):
       condition: Expression
       message: Optional[Expression]

       def accept(self, visitor: ASTVisitor) -> Any:
           return visitor.visit_assert_stmt(self)
   ```
2. Add the abstract visitor method to `ASTVisitor` in `mylang/ast.py`:
   ```python
   @abstractmethod
   def visit_assert_stmt(self, node: "AssertStmt") -> Any:
       pass
   ```
3. Add the grammar parsing method in `mylang/parser.py`.
4. Implement `visit_assert_stmt` in `mylang/evaluator.py`.

### 3. Implementing New AST Passes (Type Checker, Bytecode VM)

Because all AST nodes implement `accept(visitor: ASTVisitor)`, creating a completely new pass (e.g. a static analyzer, linter, or bytecode compiler) only requires subclassing `ASTVisitor`:

```python
from mylang.ast import ASTVisitor, BinaryExpr, Program

class BytecodeCompiler(ASTVisitor):
    def __init__(self):
        self.bytecode = []

    def visit_binary_expr(self, node: BinaryExpr):
        node.left.accept(self)
        node.right.accept(self)
        self.bytecode.append(f"OP_{node.operator.name}")
```

The parser and AST remain completely untouched!

### 4. Adding Standard Library Built-ins

Register new built-ins in `Evaluator._register_builtins()` in `mylang/evaluator.py`:

```python
def b_sqrt(evaluator, args, loc):
    import math
    return math.sqrt(args[0])

env.define("sqrt", MyLangBuiltin("sqrt", b_sqrt, expected_arity=1))
```

---

## Roadmap

- [x] Lexer with full token set, string escapes, and source location tracking
- [x] Recursive descent parser with operator precedence
- [x] Visitor-pattern AST with clean node definitions
- [x] Lexical environments, variable bindings, and constants
- [x] First-class functions, anonymous lambdas, and closures
- [x] While and Range For loops (`to` / `by`) with break and continue
- [x] List literals, indexing, and list operations
- [x] Informative error reporting with line/column carets
- [x] Interactive REPL with auto-print and inspection tools
- [ ] Dictionaries / Hash Maps (`{ "key": value }`)
- [ ] Module system (`import "math.ml"`)
- [ ] Stack-based Bytecode Virtual Machine (VM)
