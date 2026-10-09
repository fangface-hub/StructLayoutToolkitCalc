"""Tests for the SltEval class in sltcalc."""
from dataclasses import dataclass

import pytest

from sltcalc import SAFE_FUNCS, SltEval


def test_safe_funcs_is_publicly_exported():
    """Test that SAFE_FUNCS is available from the package API."""
    assert SAFE_FUNCS["abs"](-3) == 3


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        ("1 + 2 * 3", 7),
        ("7 // 2", 3),
        ("2 ** 5", 32),
        ("17 % 5", 2),
        ("8 >> 1", 4),
        ("3 << 2", 12),
        ("5 & 3", 1),
        ("5 | 2", 7),
        ("5 ^ 3", 6),
        ("+4", 4),
        ("-4", -4),
        ("10 / 4", 2.5),
    ],
)
def test_eval_basic_operations(expr, expected):
    """Test that SltEval correctly evaluates basic mathematical operations."""
    evaluator = SltEval()
    assert evaluator.eval(expr) == expected


def test_eval_uses_environment_variables():
    """Test that SltEval correctly uses environment variables in expressions."""
    evaluator = SltEval({"offset": 8, "width": 3})
    assert evaluator.eval("offset + width * 2") == 14


def test_eval_uses_dataclass_attributes():
    """Test that SltEval can use attributes from dataclass values."""

    @dataclass
    class Layout:
        offset: int
        width: int

    evaluator = SltEval({"layout": Layout(offset=8, width=3)})
    assert evaluator.eval("layout.offset + layout.width * 2") == 14


@pytest.mark.parametrize(
    ("env", "expr", "expected"),
    [
        ({
            "flag": True
        }, "1 if flag else 0", 1),
        ({
            "flag": False
        }, "1 if flag else 0", 0),
        ({}, "1 if 2 > 1 else 0", 1),
        ({}, "1 if 2 < 1 else 0", 0),
        ({
            "x": 8
        }, "99 if x >= 8 else -1", 99),
        ({
            "x": 7
        }, "99 if x >= 8 else -1", -1),
    ],
)
def test_eval_conditional_expression(env, expr, expected):
    """Test that SltEval correctly evaluates conditional expressions."""
    evaluator = SltEval(env)
    assert evaluator.eval(expr) == expected


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        ("2 > 1", True),
        ("2 < 1", False),
        ("10 >= 10", True),
        ("10 != 10", False),
        ("1 < 2 < 3", True),
        ("1 < 2 > 3", False),
        ("1 is 1", True),
        ("1 is not 2", True),
        ("2 in [1, 2, 3]", True),
        ("9 not in [1, 2, 3]", True),
    ],
)
def test_eval_comparison_expression(expr, expected):
    """Test that SltEval correctly evaluates comparison expressions."""
    evaluator = SltEval()
    assert evaluator.eval(expr) is expected


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        ("True and 1", 1),
        ("False and 1", False),
        ("0 or 5", 5),
        ("3 or 5", 3),
        ("not 0", True),
        ("not 1", False),
    ],
)
def test_eval_boolean_operators(expr, expected):
    """Test that SltEval correctly evaluates boolean operators."""
    evaluator = SltEval()
    assert evaluator.eval(expr) == expected


def test_eval_call_with_unsupported_callable_expression_raises_value_error():
    """Test that SltEval rejects non-name callable expressions."""
    evaluator = SltEval()
    with pytest.raises(ValueError, match="Unsupported expression"):
        evaluator.eval("(lambda x: x)(1)")


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        ("abs(-10)", 10),
        ("sum([1, 2, 3])", 6),
        ("len([1, 2, 3])", 3),
        ("round(3.14159, 2)", 3.14),
        ("min(3, 1, 9)", 1),
        ("max(3, 1, 9)", 9),
        ("max(2, abs(-5))", 5),
    ],
)
def test_eval_safe_functions(expr, expected):
    """Test that SltEval correctly evaluates allowed function calls."""
    evaluator = SltEval()
    assert evaluator.eval(expr) == expected


def test_eval_raises_name_error_for_undefined_variable():
    """Test that SltEval raises a NameError for undefined variables."""
    evaluator = SltEval()
    with pytest.raises(NameError, match="Undefined variable: unknown"):
        evaluator.eval("unknown + 1")


def test_eval_raises_value_error_for_unsafe_function():
    """Test that SltEval raises a ValueError for unsafe functions."""
    evaluator = SltEval()
    with pytest.raises(ValueError, match="Unsafe function: open"):
        evaluator.eval("open('dummy.txt')")


def test_eval_uses_callable_from_environment():
    """Test that SltEval can call callables provided through env."""

    def triple(x):
        return x * 3

    evaluator = SltEval({"triple": triple})
    assert evaluator.eval("triple(4)") == 12


def test_eval_raises_value_error_for_unsupported_expression():
    """Test that SltEval raises a ValueError for unsupported expressions."""
    evaluator = SltEval()
    # Set literals are intentionally unsupported by the evaluator.
    with pytest.raises(ValueError, match="Unsupported expression"):
        evaluator.eval("{1, 2, 3}")


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        ("[1, 2, 3]", [1, 2, 3]),
        ("{'a': 1, 'b': 2}", {
            "a": 1,
            "b": 2
        }),
        ("(1, 2, 3)", (1, 2, 3)),
        ("[1, 2, 3][1]", 2),
        ("[1, 2, 3, 4][1:3]", [2, 3]),
        ("[1, 2, 3, 4][:2]", [1, 2]),
        ("[1, 2, 3, 4][::2]", [1, 3]),
        ("[1, 2, 3, 4][-2:]", [3, 4]),
        ("[1, 2, 3, 4][::-1]", [4, 3, 2, 1]),
        ("{'a': 10, 'b': 20}['b']", 20),
        ("('x', 'y', 'z')[2]", "z"),
        ("('x', 'y', 'z')[1:]", ("y", "z")),
        ("{'items': [4, 5, 6]}['items'][0]", 4),
    ],
)
def test_eval_collections_and_subscript(expr, expected):
    """Test that SltEval supports collection literals, indexing, and slicing."""
    evaluator = SltEval()
    assert evaluator.eval(expr) == expected


def test_eval_subscript_with_environment_variable():
    """Test indexing and slicing collections from environment variables."""
    evaluator = SltEval({"arr": [10, 20, 30], "mapping": {"k": 7}})
    assert evaluator.eval("arr[2]") == 30
    assert evaluator.eval("arr[1:]") == [20, 30]
    assert evaluator.eval("mapping['k']") == 7
