"""Safe, deterministic expression evaluator for computing bit‑accurate
   offsets, sizes, and field values within StructLayoutToolkit."""
import ast
import operator
from functools import lru_cache

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.Is: operator.is_,
    ast.IsNot: operator.is_not,
    ast.In: lambda left, right: left in right,
    ast.NotIn: lambda left, right: left not in right,
    ast.BitAnd: operator.and_,
    ast.BitOr: operator.or_,
    ast.BitXor: operator.xor,
    ast.LShift: operator.lshift,
    ast.RShift: operator.rshift,
}

UNARY = {
    ast.UAdd: lambda x: x,
    ast.USub: lambda x: -x,
    ast.Not: lambda x: not x,
}

SAFE_FUNCS = {
    "abs": abs,
    "all": all,
    "any": any,
    "len": len,
    "min": min,
    "max": max,
    "round": round,
    "sorted": sorted,
    "sum": sum,
}


@lru_cache(maxsize=2048)
def _parse(expr: str) -> ast.AST:
    """Parse an expression once; the tree is never mutated."""
    return ast.parse(expr, mode="eval").body


class SltEval:
    """A safe, deterministic expression evaluator for computing bit‑accurate
       offsets, sizes, and field values within StructLayoutToolkit."""

    def __init__(self, env=None):
        self.env = env or {}

    def eval(self, expr: str) -> any:
        """Evaluate a mathematical expression in a safe and deterministic
           manner.
        Args:
            expr (str): The mathematical expression to evaluate.

        Returns:
            The result of the evaluated expression.
        """
        return self._eval(_parse(expr))

    def _eval(self, node) -> any:
        """Recursively evaluate an AST node."""
        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Name):
            if node.id not in self.env:
                raise NameError(f"Undefined variable: {node.id}")
            return self.env[node.id]

        if isinstance(node, ast.Attribute):
            return getattr(self._eval(node.value), node.attr)

        if isinstance(node, ast.List):
            return [self._eval(element) for element in node.elts]

        if isinstance(node, ast.Tuple):
            return tuple(self._eval(element) for element in node.elts)

        if isinstance(node, ast.Slice):
            return slice(
                self._eval(node.lower) if node.lower is not None else None,
                self._eval(node.upper) if node.upper is not None else None,
                self._eval(node.step) if node.step is not None else None,
            )

        if isinstance(node, ast.Dict):
            return {
                self._eval(key): self._eval(value)
                for key, value in zip(node.keys, node.values)
            }

        if isinstance(node, ast.BinOp):
            op = OPS[type(node.op)]
            return op(self._eval(node.left), self._eval(node.right))

        if isinstance(node, ast.UnaryOp):
            op = UNARY[type(node.op)]
            return op(self._eval(node.operand))

        if isinstance(node, ast.IfExp):
            cond = self._eval(node.test)
            return self._eval(node.body if cond else node.orelse)

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                result = self._eval(node.values[0])
                for value_node in node.values[1:]:
                    if not result:
                        return result
                    result = self._eval(value_node)
                return result

            if isinstance(node.op, ast.Or):
                result = self._eval(node.values[0])
                for value_node in node.values[1:]:
                    if result:
                        return result
                    result = self._eval(value_node)
                return result

            raise ValueError(f"Unsupported expression: {ast.dump(node)}")

        if isinstance(node, ast.Compare):
            left = self._eval(node.left)
            for op_node, comparator in zip(node.ops, node.comparators):
                op = OPS.get(type(op_node))
                if op is None:
                    raise ValueError(
                        f"Unsupported expression: {ast.dump(node)}")
                right = self._eval(comparator)
                if not op(left, right):
                    return False
                left = right
            return True

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError(f"Unsupported expression: {ast.dump(node)}")

            func = SAFE_FUNCS.get(node.func.id)
            if func is None and node.func.id in self.env:
                env_func = self.env[node.func.id]
                if callable(env_func):
                    func = env_func

            if func is None:
                raise ValueError(f"Unsafe function: {node.func.id}")
            args = [self._eval(a) for a in node.args]
            return func(*args)

        if isinstance(node, ast.Subscript):
            value = self._eval(node.value)
            index = self._eval(node.slice)
            return value[index]

        raise ValueError(f"Unsupported expression: {ast.dump(node)}")
