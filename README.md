# StructLayoutToolkitCalc

A safe, deterministic expression evaluator for computing bit‑accurate offsets, sizes, and field values within StructLayoutToolkit.

## Overview

sltcalc provides a safe and deterministic expression evaluator used across StructLayoutToolkit to compute bit‑accurate offsets, sizes, and derived field values.
It parses expressions into Python’s AST and evaluates a restricted subset of operations, ensuring predictable behavior without accessing Python globals or executing arbitrary code.
The evaluator supports arithmetic, bitwise operations, conditional expressions, and user‑defined variables supplied through an isolated environment.
This module enables dynamic field definitions, computed offsets, variable‑length structures, and protocol‑specific formulas while maintaining strict safety and structural consistency.

## Usage

### Basic

```python
from sltcalc import SltEval

evaluator = SltEval()
result = evaluator.eval("1 + 2 * 3")
print(result)  # 7
```

### With variables

```python
from sltcalc import SltEval

env = {
    "offset": 8,
    "width": 3,
    "flag": True,
}

evaluator = SltEval(env)

print(evaluator.eval("offset + width * 2"))       # 14
print(evaluator.eval("1 if flag else 0"))         # 1
print(evaluator.eval("99 if offset >= 8 else -1"))  # 99
```

### Error behavior

```python
from sltcalc import SltEval

evaluator = SltEval()

# NameError: undefined variable
evaluator.eval("unknown + 1")

# ValueError: unsafe function
evaluator.eval("sum(1, 2)")
```

## Supported expressions

SltEval evaluates a restricted subset of Python expression AST nodes.

### Literals

- Numeric constants (for example: 0, 42, 3.5)
- Boolean constants (True, False)
- List literals (for example: [1, 2, 3])
- Tuple literals (for example: (1, 2, 3))
- Dict literals (for example: {"a": 1, "b": 2})

### Variables

- Variable lookup from the evaluator environment (SltEval(env))
- Attribute access on environment values (for example: obj.value)

### Binary operators

- Arithmetic: +, -, *, /, //, %, **
- Bitwise: &, |, ^, <<, >>

### Unary operators

- Unary plus: +x
- Unary minus: -x
- Boolean negation: not x

### Boolean operators

- and
- or

### Comparisons

- ==, !=, <, <=, >, >=, is, is not, in, not in
- Chained comparisons are supported (for example: 1 < 2 < 3)

### Conditional expression

- Ternary expression: a if condition else b

### Attribute and subscript access

- Index/key access (for example: arr[0], mapping["key"])
- Slicing (for example: arr[1:4], arr[:3], arr[::2], arr[::-1])
- Slice bounds and steps may be omitted; negative indices and steps follow Python sequence semantics
- Attribute access is supported (for example: obj.value)
- Nested access is supported (for example: access key "items" and then index 0)

### Function calls

- Built-in allowlist: abs(...), all(...), any(...), len(...),
    bytes(...), bytearray(...), min(...), max(...), round(...),
    sorted(...), sum(...)
- Callables passed through environment are allowed
    (for example: SltEval({"triple": triple}) then triple(4))
- Byte strings and byte arrays can be compared using standard comparison operators.

## Not supported

- Set literals in expressions
- Non-name call targets (for example: (lambda x: x)(1))

Unsupported constructs raise ValueError with an Unsupported expression message.

## Testing

Run the complete test suite:

```powershell
uv run pytest -q
```

Generate a branch coverage report in the terminal:

```powershell
uv run pytest --cov=sltcalc --cov-branch --cov-report=term-missing -q
```

Generate a browsable HTML coverage report in `htmlcov/`:

```powershell
uv run pytest --cov=sltcalc --cov-branch --cov-report=html -q
```

Open `htmlcov/index.html` in a browser to inspect uncovered lines and branches.
